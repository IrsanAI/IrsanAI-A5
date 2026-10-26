
import pathlib, time, json, hashlib, os

def get_live_nonce_path():
    return pathlib.Path.home() / "a5_evidence" / ".live_nonce"

def get_local_target_hash() -> str:
    # Production v3.3: APK-first streaming SHA (1MiB chunks) – OOM safe
    import pathlib, hashlib
    for apk in pathlib.Path.home().glob("a5_targets/**/*.apk"):
        if apk.exists():
            try:
                h=hashlib.sha256()
                with apk.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                return h.hexdigest()
            except:
                pass
    candidates=[
        pathlib.Path.home()/ "a5_targets/spd/core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/Char.java",
        pathlib.Path("core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/Char.java"),
    ]
    for cand in list(pathlib.Path.home().glob("a5_targets/**/Char.java")):
        candidates.append(cand)
    for c in candidates:
        try:
            if c.exists():
                h=hashlib.sha256()
                with c.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                return h.hexdigest()
        except:
            pass
    return "no-target-found"

def get_local_frida_version() -> str:
    try:
        import frida
        v=getattr(frida, "__version__", "unknown")
        if v!="unknown": return v
    except: pass
    try:
        import subprocess
        out=subprocess.check_output(["frida","--version"], text=True).strip()
        if out: return out
    except: pass
    return "unknown"

def get_expected_device_id() -> str:
    try:
        import subprocess
        out=subprocess.check_output(["getprop","ro.serialno"], text=True).strip()
        if out: return out
    except: pass
    try:
        import subprocess, platform as pl
        out=subprocess.check_output(["getprop","ro.product.model"], text=True).strip()
        if out:
            return out+"-"+pl.node()
    except: pass
    import platform as pl
    return pl.node() or "unknown-device"

def count_real_observed(finding_id="spd_barrier_dr_order") -> int:
    ev_dir=pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists(): return 0
    local_hash=get_local_target_hash()
    if local_hash=="no-target-found":
        return 0
    exp_dev=get_expected_device_id()
    exp_fr=get_local_frida_version()
    now=time.time()
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
        # v3.3 crisis-proof
        src=j.get("source") or j.get("origin") or ""
        if src!="frida_js": continue
        token=j.get("frida_session_token") or j.get("session_token") or ""
        if not token: continue
        sess_file=pathlib.Path.home() / f"a5_evidence/.frida_session_{j.get('live_nonce')}"
        if not sess_file.exists(): continue
        try:
            if sess_file.read_text().strip()!=token: continue
        except: continue
        # mtime ±2s, age <30s
        try:
            sess_mtime=sess_file.stat().st_mtime
            ev_mtime=fp.stat().st_mtime
            if abs(ev_mtime - sess_mtime) > 2.5: continue
            if now - sess_mtime > 30: continue
            if now - ev_mtime > 30: continue
            ts=j.get("ts") or j.get("timestamp") or 0
            if ts>1e12: ts/=1000
            if abs(now - float(ts)) > 30: continue
        except: continue
        dev=j.get("device_id") or ""
        if "localhost" in dev: continue
        if dev=="unknown-device": continue
        if dev!=exp_dev: continue
        fr=j.get("frida_version") or ""
        if fr=="unknown" or not fr: continue
        if fr=="unknown-device": continue
        if exp_fr!="unknown" and fr!=exp_fr: continue
        sha=j.get("binary_sha256") or ""
        if not sha: continue
        if sha!=local_hash: continue
        if sha=="no-target-found": continue
        obs=j.get("observed") or {}
        if not obs.get("barrier_absorb_value"): continue
        if obs.get("order")!="dr_before_barrier": continue
        if "Barrier" not in (obs.get("barrier_class") or ""): continue
        if not obs.get("attack_id"): continue
        count+=1
    return count

class _Result(dict):
    @property
    def overall_confidence(self):
        return self.get("confidence", 0.72)
    @property
    def survival_assessment(self):
        # v2 compat: no live -> partially reframed
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
    # production wording, no demo
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
        print(f"=== Torwart v3.3 – i3 live=0 real={real} local_hash={local_hash}... ===")
        return _Result(finding_id="spd_barrier_dr_order", confidence=base_conf, mode="production", reason="awaiting live attestation", survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – SPD live attestation requires real device with Frida Gadget, currently 0.72 SECURE AWAITING LIVE ATTESTATION")
    else:
        print(f"[Torwart v3.3] live_nonce={nonce_path.read_text()[:8] if nonce_path.exists() else '-'} local_hash={local_hash}... local_frida={local_frida} real_correlated={real}")
        if real==0:
            print(f"[!] Torwart v3.3: --live 1 für spd_barrier_dr_order – no real correlated – real=0 – bleibe bei 0.72")
            return _Result(finding_id="spd_barrier_dr_order", confidence=0.72, mode="production", real=real, survival_assessment="partially reframed", phase0_access_limitations="nicht implementiert / not implemented – awaiting live attestation, real_correlated=0")
        else:
            print(f"[+] Torwart v3.3: ATTESTED LIVE – real={real} → 0.88")
            return _Result(finding_id="spd_barrier_dr_order", confidence=0.88, mode="production", real=real, survival_assessment="attested", phase0_access_limitations="attested live – production ready")

def run_spd_barrier_dr_residual_i3(live):
    return run_spd_barrier_dr_residual(live)
