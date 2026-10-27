
import pathlib, time, json, hashlib, os, hmac, uuid as uuid_mod
from .targets.spd import PKG as SPD_PKG, FINDING_ID as SPD_FINDING, is_valid_target_file, validate_observed, is_target_process, is_valid_target_name

def get_live_nonce_path():
    return pathlib.Path.home() / "a5_evidence" / ".live_nonce"

def get_runner_secret_path():
    return pathlib.Path.home() / "a5_evidence" / ".runner_secret"

def get_local_target_hash_verbose():
    log=[]
    for apk in (pathlib.Path.home() / "a5_targets").rglob("*.apk"):
        if not apk.is_file(): continue
        try:
            if apk.stat().st_size < 1_000_000:
                log.append(f"skip apk {apk} <1MB")
                continue
            h=hashlib.sha256()
            with apk.open('rb') as f:
                for chunk in iter(lambda: f.read(1024*1024), b''):
                    h.update(chunk)
            return h.hexdigest(), log
        except Exception as e:
            log.append(f"apk hash error {apk}: {e}")
    base = pathlib.Path.home() / "a5_targets"
    if base.exists():
        for c in base.rglob("Char.java"):
            try:
                if not is_valid_target_file(c):
                    log.append(f"Char.java invalid marker {c}")
                    continue
                h=hashlib.sha256()
                with c.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                return h.hexdigest(), log
            except Exception as e:
                log.append(f"Char.java error {c}: {e}")
                continue
    return "no-target-found", log+["no valid target"]

def get_local_target_hash() -> str:
    h,_ = get_local_target_hash_verbose()
    return h

def get_local_frida_version() -> str:
    try:
        import frida
        v=getattr(frida, "__version__", "unknown")
        if v!="unknown": return v
    except Exception:
        pass
    return "unknown"  # v4.3.4 no subprocess – avoids segfault on Termux 17.2.14

def get_expected_device_id() -> str:
    try:
        import subprocess
        out=subprocess.check_output(["getprop","ro.serialno"], text=True, timeout=1).strip()
        if out: return out
    except Exception:
        pass
    try:
        import subprocess, platform as pl
        out=subprocess.check_output(["getprop","ro.product.model"], text=True, timeout=1).strip()
        if out:
            return out+"-"+pl.node()
    except Exception:
        pass
    import platform as pl
    return pl.node() or "unknown-device"

def is_frida_live_verbose():
    log=[]
    try:
        import frida
        dm = frida.get_device_manager()
        devices = dm.enumerate_devices()
        log.append(f"frida devices: {len(devices)}")
        for dev in devices:
            try:
                procs = dev.enumerate_processes()
                for p in procs:
                    if is_target_process(p.name):
                        log.append(f"found SPD process {p.name} pid={p.pid} on {dev.id}")
                        return True, log
            except Exception as e:
                log.append(f"enumerate_processes fail on {dev}: {e}")
                continue
    except Exception as e:
        log.append(f"frida not live: {e}")
    try:
        priv_dir = pathlib.Path(f"/data/data/{SPD_PKG}/files")
        if priv_dir.exists():
            for f in priv_dir.glob(".a5_frida_token_*"):
                try:
                    age = time.time() - f.stat().st_mtime
                    if age > 30:
                        log.append(f"private token too old {age}s {f}")
                        continue
                    try:
                        if f.stat().st_uid != os.getuid():
                            log.append(f"private token owned by app UID {f.stat().st_uid} != {os.getuid()} – valid live signal")
                            return True, log
                        else:
                            log.append(f"private token same UID {f} – ignored in prod (sandbox root)")
                    except Exception as e:
                        log.append(f"stat fail {f}: {e}")
                except Exception as e:
                    log.append(f"private token check fail {f}: {e}")
    except Exception as e:
        log.append(f"private dir check fail: {e}")
    log.append("is_frida_live=False – no SPD process found")
    return False, log

def is_frida_live() -> bool:
    v,_ = is_frida_live_verbose()
    return v

def count_real_observed_verbose(finding_id=SPD_FINDING):
    ev_dir=pathlib.Path.home() / "a5_evidence"
    rejections=[]
    if not ev_dir.exists():
        return 0, [("ev_dir missing", str(ev_dir))]
    local_hash, hash_log = get_local_target_hash_verbose()
    if local_hash=="no-target-found":
        return 0, [("no-target-found", "; ".join(hash_log))]
    live, live_log = is_frida_live_verbose()
    if not live:
        return 0, [("is_frida_live=False", "; ".join(live_log))]
    exp_dev=get_expected_device_id()
    exp_fr=get_local_frida_version()
    now=time.time()
    secret_path=get_runner_secret_path()
    runner_secret=None
    if secret_path.exists():
        try:
            runner_secret=secret_path.read_text().strip()
        except Exception as e:
            rejections.append((f"{secret_path} read fail", str(e)))
    else:
        rejections.append(("runner_secret missing", str(secret_path)))
    count=0
    files=list(ev_dir.glob("*.json"))
    if not files:
        rejections.append(("no json files", str(ev_dir)))
    for fp in files:
        try:
            j=json.loads(fp.read_text())
        except Exception as e:
            rejections.append((f"{fp.name} json parse", str(e)))
            continue
        if j.get("finding_id")!=finding_id:
            rejections.append((f"{fp.name} finding_id", f"{j.get('finding_id')} != {finding_id}"))
            continue
        if j.get("provider")!="a3_frida":
            rejections.append((f"{fp.name} provider", str(j.get("provider"))))
            continue
        # Le Chat Fix #3: target check via plugin, not hardcoded in core string compare
        if not is_valid_target_name(j.get("target")):
            rejections.append((f"{fp.name} target", f"{j.get('target')} != {SPD_FINDING.split('_')[0]} plugin"))
            continue
        if j.get("confidence")!="observed":
            rejections.append((f"{fp.name} confidence", str(j.get("confidence"))))
            continue
        if not j.get("correlated"):
            rejections.append((f"{fp.name} correlated", "false"))
            continue
        if j.get("fixture"):
            rejections.append((f"{fp.name} fixture", "is fixture"))
            continue
        if not j.get("live_nonce"):
            rejections.append((f"{fp.name} live_nonce", "missing"))
            continue
        if j.get("source")!="frida_js":
            rejections.append((f"{fp.name} source", str(j.get("source"))))
            continue
        if j.get("java_uuid_source")!="java.util.UUID":
            rejections.append((f"{fp.name} java_uuid_source", str(j.get("java_uuid_source"))))
            continue
        token=j.get("frida_session_token") or ""
        if not token:
            rejections.append((f"{fp.name} token", "missing"))
            continue
        try:
            u=uuid_mod.UUID(token)
            if u.version!=4:
                rejections.append((f"{fp.name} token version", f"{u.version} != 4"))
                continue
        except Exception as e:
            rejections.append((f"{fp.name} token uuid", str(e)))
            continue
        sess_file=ev_dir / f".frida_session_{j.get('live_nonce')}"
        if not sess_file.exists():
            rejections.append((f"{fp.name} session file", f"missing {sess_file.name}"))
            continue
        try:
            raw = sess_file.read_text().strip()
            if raw.startswith("{"):
                rejections.append((f"{fp.name} session format", "JSON instead of raw token – F2 enforced"))
                continue
            if raw != token:
                rejections.append((f"{fp.name} session mismatch", "token mismatch"))
                continue
        except Exception as e:
            rejections.append((f"{fp.name} session read", str(e)))
            continue
        try:
            nonce_path=get_live_nonce_path()
            if not nonce_path.exists():
                rejections.append((f"{fp.name} nonce file", "missing"))
                continue
            if nonce_path.read_text().strip()!=j.get("live_nonce"):
                rejections.append((f"{fp.name} nonce mismatch", ""))
                continue
            sess_mtime=sess_file.stat().st_mtime
            ev_mtime=fp.stat().st_mtime
            nonce_mtime=nonce_path.stat().st_mtime
            # Le Chat Fix #5: comment matches behavior – fail-closed ordering check is enforced
            if not (nonce_mtime <= sess_mtime <= ev_mtime):
                rejections.append((f"{fp.name} mtime order", f"ordering fail: nonce<=sess<=ev must hold – fail-closed"))
                continue
            if abs(ev_mtime - sess_mtime) > 2.5:
                rejections.append((f"{fp.name} ev-sess delta", f"{abs(ev_mtime-sess_mtime)} >2.5s"))
                continue
            if abs(sess_mtime - nonce_mtime) > 5:
                rejections.append((f"{fp.name} sess-nonce delta", f"{abs(sess_mtime-nonce_mtime)} >5s"))
                continue
            if now - sess_mtime > 30:
                rejections.append((f"{fp.name} sess age", f"{now-sess_mtime}s >30"))
                continue
            if now - ev_mtime > 30:
                rejections.append((f"{fp.name} ev age", f"{now-ev_mtime}s >30"))
                continue
            if now - nonce_mtime > 35:
                rejections.append((f"{fp.name} nonce age", f"{now-nonce_mtime}s >35"))
                continue
            ts=j.get("ts") or j.get("timestamp") or 0
            if ts>1e12: ts/=1000
            if abs(now - float(ts)) > 30:
                rejections.append((f"{fp.name} ts delta", f"{abs(now-float(ts))} >30s"))
                continue
        except Exception as e:
            rejections.append((f"{fp.name} time check", str(e)))
            continue
        dev=j.get("device_id") or ""
        if "localhost" in dev.lower():
            rejections.append((f"{fp.name} device localhost", dev))
            continue
        if dev=="unknown-device":
            rejections.append((f"{fp.name} device unknown", dev))
            continue
        if dev!=exp_dev:
            rejections.append((f"{fp.name} device mismatch", f"{dev} != {exp_dev}"))
            continue
        fr=j.get("frida_version") or ""
        if fr=="unknown" or not fr:
            rejections.append((f"{fp.name} frida_version", str(fr)))
            continue
        if exp_fr!="unknown" and fr!=exp_fr:
            rejections.append((f"{fp.name} frida_version mismatch", f"{fr} != {exp_fr}"))
            continue
        sha=j.get("binary_sha256") or ""
        if not sha or sha=="no-target-found":
            rejections.append((f"{fp.name} sha", str(sha)))
            continue
        if sha!=local_hash:
            rejections.append((f"{fp.name} sha mismatch", f"{sha[:12]} != {local_hash[:12]}"))
            continue
        obs=j.get("observed") or {}
        ok, reason = validate_observed(obs)
        if not ok:
            rejections.append((f"{fp.name} observed", reason))
            continue
        if not runner_secret:
            rejections.append((f"{fp.name} runner_secret", "missing – cannot verify HMAC, see THREAT_MODEL"))
            continue
        # Le Chat Fix #1 + #5: canonical delimiter + no expected HMAC in log
        canonical = f"{token}|{j.get('live_nonce')}|{obs.get('attack_id')}"
        expected_hmac = hmac.new(runner_secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        # constant-time compare
        if not hmac.compare_digest(j.get("runner_hmac") or "", expected_hmac):
            # FIX: do NOT leak expected_hmac prefix – just "hmac invalid"
            rejections.append((f"{fp.name} hmac", "hmac invalid"))
            continue
        if not j.get("runner_verified"):
            rejections.append((f"{fp.name} runner_verified", "false"))
            continue
        try:
            priv = pathlib.Path(f"/data/data/{SPD_PKG}/files/.a5_frida_token_{j.get('live_nonce')}")
            if priv.exists():
                if priv.read_text().strip()!=token:
                    rejections.append((f"{fp.name} private token mismatch", ""))
                    continue
        except Exception as e:
            rejections.append((f"{fp.name} private token check", str(e)))
            continue
        count+=1
    return count, rejections

def count_real_observed(finding_id=SPD_FINDING) -> int:
    c,_ = count_real_observed_verbose(finding_id)
    return c

class _Result(dict):
    @property
    def overall_confidence(self):
        return self.get("confidence", 0.72)
    @property
    def survival_assessment(self):
        return self.get("survival_assessment", "partially reframed")
    @property
    def phase0_access_limitations(self):
        return self.get("phase0_access_limitations", "nicht implementiert / not implemented – awaiting live Frida attestation")
    @property
    def residual(self):
        return self.get("real", 0)
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

def run_spd_barrier_dr_residual(live=0):
    real, rej = count_real_observed_verbose()
    base_conf=0.72
    local_hash, _ = get_local_target_hash_verbose()
    lh = local_hash[:12]
    local_frida=get_local_frida_version()
    nonce_path=get_live_nonce_path()
    if live==0:
        print(f"=== Torwart v4.3 – i3 live=0 real={real} local_hash={lh}... ===")
        if rej:
            print(f"[debug] rejections: {rej[:3]}")
        return _Result(finding_id=SPD_FINDING, confidence=base_conf, mode="production", reason="awaiting live attestation", survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – SPD live attestation requires real device with Frida, 0.72 SECURE AWAITING LIVE ATTESTATION – v4.3 Le Chat blockers fixed", rejections=rej)
    else:
        print(f"[Torwart v4.3] live_nonce={nonce_path.read_text()[:8] if nonce_path.exists() else '-'} local_hash={lh}... local_frida={local_frida} real_correlated={real}")
        if real==0:
            print(f"[!] Torwart v4.3: --live 1 – no real correlated – real=0 – bleibe bei 0.72")
            for r in rej[:5]:
                print(f"  - reject: {r}")
            return _Result(finding_id=SPD_FINDING, confidence=0.72, mode="production", real=real, survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – awaiting live attestation, real_correlated=0 – v4.3 fail-closed, see THREAT_MODEL.md", rejections=rej)
        else:
            print(f"[+] Torwart v4.3: ATTESTED LIVE – real={real} → 0.88")
            return _Result(finding_id=SPD_FINDING, confidence=0.88, mode="production", real=real, survival_assessment="attested", phase0_access_limitations="attested live – production ready v4.3")

def run_spd_barrier_dr_residual_i3(live):
    return run_spd_barrier_dr_residual(live)
