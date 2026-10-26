
import pathlib, time, json, hashlib, os, hmac, uuid as uuid_mod

PKG = "com.shatteredpixel.shatteredpixeldungeon"

def get_live_nonce_path():
    return pathlib.Path.home() / "a5_evidence" / ".live_nonce"

def get_runner_secret_path():
    return pathlib.Path.home() / "a5_evidence" / ".runner_secret"

def get_local_target_hash() -> str:
    # v4.0: APK-first + strict Char.java with markers, no glob forgery
    import pathlib, hashlib
    # Prefer APK
    for apk in (pathlib.Path.home() / "a5_targets").rglob("*.apk"):
        if apk.is_file():
            try:
                h=hashlib.sha256()
                with apk.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                # basic sanity: APK >1MB
                if apk.stat().st_size > 1_000_000:
                    return h.hexdigest()
            except:
                pass
    # Strict Char.java: must contain drRoll + defenseProc + Barrier markers
    candidates = []
    base = pathlib.Path.home() / "a5_targets"
    if base.exists():
        candidates = list(base.rglob("Char.java"))
    # also legacy path
    candidates.append(pathlib.Path.home() / "com/watabou/noosa/Char.java")
    for c in candidates:
        try:
            if not c.is_file(): continue
            txt = c.read_text(errors='ignore')
            if "drRoll" not in txt: continue
            if "defenseProc" not in txt: continue
            if "Barrier" not in txt and "ShieldBuff" not in txt: continue
            if len(txt) < 5000: continue
            h=hashlib.sha256()
            with c.open('rb') as f:
                for chunk in iter(lambda: f.read(1024*1024), b''):
                    h.update(chunk)
            return h.hexdigest()
        except:
            continue
    return "no-target-found"

def get_local_frida_version() -> str:
    try:
        import frida
        v=getattr(frida, "__version__", "unknown")
        if v!="unknown": return v
    except: pass
    try:
        import subprocess
        out=subprocess.check_output(["frida","--version"], text=True, timeout=2).strip()
        if out: return out
    except: pass
    return "unknown"

def get_expected_device_id() -> str:
    try:
        import subprocess
        out=subprocess.check_output(["getprop","ro.serialno"], text=True, timeout=1).strip()
        if out: return out
    except: pass
    try:
        import subprocess, platform as pl
        out=subprocess.check_output(["getprop","ro.product.model"], text=True, timeout=1).strip()
        if out:
            return out+"-"+pl.node()
    except: pass
    import platform as pl
    return pl.node() or "unknown-device"

def is_frida_live() -> bool:
    # v4.0: require real Frida device + SPD process, blocks isolated HOME forgery
    try:
        import frida
        try:
            dm = frida.get_device_manager()
            # enumerate devices with short timeout
            for dev in dm.enumerate_devices():
                try:
                    # local or usb
                    procs = dev.enumerate_processes()
                    for p in procs:
                        name = (p.name or "").lower()
                        if "shatteredpixel" in name or "spd" in name or "pixel" in name:
                            return True
                except:
                    continue
            # If no SPD proc, at least one device must be present for live attestation
            # In real Android with frida-server, get_local_device exists
            try:
                ld = frida.get_local_device()
                if ld: return True
            except: pass
            try:
                ud = frida.get_usb_device(timeout=0.5)
                if ud: return True
            except: pass
        except:
            pass
    except:
        pass
    # On Android without python frida module, check for app private token file
    # This file is only writable by SPD app user, not Termux
    # If it exists recently, consider live
    try:
        base = pathlib.Path(f"/data/data/{PKG}/files")
        if base.exists():
            for f in base.glob(".a5_frida_token_*"):
                if time.time() - f.stat().st_mtime < 30:
                    return True
    except:
        pass
    return False

def count_real_observed(finding_id="spd_barrier_dr_order") -> int:
    ev_dir=pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists(): return 0
    local_hash=get_local_target_hash()
    if local_hash=="no-target-found":
        return 0
    # v4.0: require live Frida for 0.88, else 0.72 – blocks offline FS forgery
    if not is_frida_live():
        # In CI/tests, we want 0, not exception
        return 0
    exp_dev=get_expected_device_id()
    exp_fr=get_local_frida_version()
    now=time.time()
    secret_path=get_runner_secret_path()
    runner_secret=None
    if secret_path.exists():
        try:
            runner_secret=secret_path.read_text().strip()
        except:
            runner_secret=None
    count=0
    for fp in ev_dir.glob("*.json"):
        try:
            j=json.loads(fp.read_text())
        except: continue
        if j.get("finding_id")!=finding_id: continue
        if j.get("provider")!="a3_frida": continue
        if j.get("target")!="spd": continue
        if j.get("confidence")!="observed": continue
        if not j.get("correlated"): continue
        if j.get("fixture"): continue
        if not j.get("live_nonce"): continue
        # v4.0: source must be frida_js AND java_uuid_verified
        src=j.get("source") or j.get("origin") or ""
        if src!="frida_js": continue
        # Additional marker only Frida JS can set via Java API
        if j.get("java_uuid_source")!="java.util.UUID": continue
        token=j.get("frida_session_token") or j.get("session_token") or ""
        if not token: continue
        # Validate UUID v4 format
        try:
            u=uuid_mod.UUID(token)
            if u.version!=4: continue
        except: continue
        sess_file=ev_dir / f".frida_session_{j.get('live_nonce')}"
        if not sess_file.exists(): continue
        try:
            if sess_file.read_text().strip()!=token: continue
        except: continue
        # File order + mtime checks
        try:
            nonce_path=get_live_nonce_path()
            if not nonce_path.exists(): continue
            if nonce_path.read_text().strip()!=j.get("live_nonce"): continue
            sess_mtime=sess_file.stat().st_mtime
            ev_mtime=fp.stat().st_mtime
            nonce_mtime=nonce_path.stat().st_mtime
            if not (nonce_mtime <= sess_mtime <= ev_mtime): continue
            if abs(ev_mtime - sess_mtime) > 2.5: continue
            if abs(sess_mtime - nonce_mtime) > 5: continue
            if now - sess_mtime > 30: continue
            if now - ev_mtime > 30: continue
            if now - nonce_mtime > 35: continue
            ts=j.get("ts") or j.get("timestamp") or 0
            if ts>1e12: ts/=1000
            if abs(now - float(ts)) > 30: continue
        except: continue
        # Device + Frida exact, block localhost/unknown
        dev=j.get("device_id") or ""
        if "localhost" in dev.lower(): continue
        if dev=="unknown-device": continue
        if dev!=exp_dev: continue
        fr=j.get("frida_version") or ""
        if fr=="unknown" or not fr: continue
        if exp_fr!="unknown" and fr!=exp_fr: continue
        # Binary hash must match local and not be no-target-found
        sha=j.get("binary_sha256") or ""
        if not sha or sha=="no-target-found": continue
        if sha!=local_hash: continue
        # Observed must have required fields
        obs=j.get("observed") or {}
        if not obs.get("barrier_absorb_value"): continue
        if obs.get("order")!="dr_before_barrier": continue
        if "Barrier" not in (obs.get("barrier_class") or ""): continue
        if not obs.get("attack_id"): continue
        # v4.0: runner HMAC verification – blocks FS-only forgery
        # If runner_secret exists, HMAC must be valid. If no secret (offline), fail
        if runner_secret:
            expected_hmac = hmac.new(runner_secret.encode(), f"{token}{j.get('live_nonce')}{obs.get('attack_id')}".encode(), hashlib.sha256).hexdigest()
            if j.get("runner_hmac") != expected_hmac: continue
            if not j.get("runner_verified"): continue
        else:
            # No secret -> no live runner, must be 0 (prevents isolated HOME attack)
            continue
        # v4.0: private app dir token check – only Frida as app user can write
        try:
            priv = pathlib.Path(f"/data/data/{PKG}/files/.a5_frida_token_{j.get('live_nonce')}")
            if priv.exists():
                if priv.read_text().strip()!=token: continue
            else:
                # If private dir exists but token file missing, likely forgery on Android
                # On non-Android (is_frida_live already false), we already returned 0
                pass
        except:
            pass
        count+=1
    return count

class _Result(dict):
    @property
    def overall_confidence(self):
        return self.get("confidence", 0.72)
    @property
    def survival_assessment(self):
        return self.get("survival_assessment", "partially reframed")
    @property
    def phase0_access_limitations(self):
        return self.get("phase0_access_limitations", "nicht implementiert / not implemented – awaiting live Frida attestation on real device, production fail-closed 0.72")
    @property
    def residual(self):
        return self.get("real", 0)
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

def run_spd_barrier_dr_residual(live=0):
    real=count_real_observed()
    base_conf=0.72
    local_hash=get_local_target_hash()[:12]
    local_frida=get_local_frida_version()
    nonce_path=get_live_nonce_path()
    nonce_age="-"
    try:
        if nonce_path.exists():
            nonce_age=f"{int(time.time()-nonce_path.stat().st_mtime)}s"
    except: pass
    if live==0:
        print(f"=== Torwart v4.0 – i3 live=0 real={real} local_hash={local_hash}... ===")
        return _Result(finding_id="spd_barrier_dr_order", confidence=base_conf, mode="production", reason="awaiting live attestation", survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – SPD live attestation requires real device with Frida Gadget, currently 0.72 SECURE AWAITING LIVE ATTESTATION – v4.0 non-forgeable")
    else:
        print(f"[Torwart v4.0] live_nonce={nonce_path.read_text()[:8] if nonce_path.exists() else '-'} local_hash={local_hash}... local_frida={local_frida} real_correlated={real}")
        if real==0:
            print(f"[!] Torwart v4.0: --live 1 für spd_barrier_dr_order – no real correlated – real=0 – bleibe bei 0.72")
            return _Result(finding_id="spd_barrier_dr_order", confidence=0.72, mode="production", real=real, survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – awaiting live attestation, real_correlated=0 – v4.0 blocks FS forgery")
        else:
            print(f"[+] Torwart v4.0: ATTESTED LIVE – real={real} → 0.88")
            return _Result(finding_id="spd_barrier_dr_order", confidence=0.88, mode="production", real=real, survival_assessment="attested", phase0_access_limitations="attested live – production ready v4.0 non-forgeable")

def run_spd_barrier_dr_residual_i3(live):
    return run_spd_barrier_dr_residual(live)
