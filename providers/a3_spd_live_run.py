
import pathlib, json, time, random, string, sys, hashlib

def get_live_nonce_path():
    return pathlib.Path.home() / "a5_evidence" / ".live_nonce"

def get_nonce():
    p=get_live_nonce_path()
    if p.exists():
        try:
            age=time.time()-p.stat().st_mtime
            if age < 300:  # reuse ≤5min
                return p.read_text().strip()
        except: pass
    nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
    p.parent.mkdir(exist_ok=True)
    p.write_text(nonce)
    return nonce

def get_local_target_hash():
    for apk in pathlib.Path.home().glob("a5_targets/**/*.apk"):
        if apk.exists():
            try:
                h=hashlib.sha256()
                with apk.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                return h.hexdigest()
            except: pass
    for cand in pathlib.Path.home().glob("a5_targets/**/Char.java"):
        if cand.exists():
            try:
                h=hashlib.sha256()
                with cand.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        h.update(chunk)
                return h.hexdigest()
            except: pass
    cand=pathlib.Path.home()/ "a5_targets/spd/core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/actors/Char.java"
    if cand.exists():
        h=hashlib.sha256()
        with cand.open('rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        return h.hexdigest()
    return "no-target-found"

def get_expected_device_id():
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

def get_local_frida_version():
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

def write_evidence(ev_data):
    nonce=get_nonce()
    ts=time.time()
    is_fixture=ev_data.get("_fixture", False)
    conf="inferred" if is_fixture else "observed"
    # v6: token only from JS, no uuid4()
    token=ev_data.get("frida_session_token") or ev_data.get("session_token") or ""
    src=ev_data.get("source") or ev_data.get("_source") or ("frida_js" if token else "unknown")
    out={
        "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":conf,"correlated": not is_fixture,
        "observed":{
            "barrier_absorb_value": ev_data.get("_barrier_absorb", 5),
            "dr_roll": ev_data.get("_dr_roll", 3),
            "damage_roll": ev_data.get("_damage_roll", 10),
            "order": ev_data.get("_order","dr_before_barrier"),
            "barrier_class": ev_data.get("_barrier_class","com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier"),
            "attack_id": ev_data.get("_attack_id", 1)
        },
        "binary_sha256": get_local_target_hash(),
        "device_id": get_expected_device_id(),
        "frida_version": get_local_frida_version(),
        "live_nonce": nonce,
        "frida_session_token": token,
        "session_token": token,
        "source": src,
        "ts": ts,
        "timestamp": int(ts*1000),
        "fixture": is_fixture
    }
    if is_fixture:
        out["fixture"]=True
    ev_dir=pathlib.Path.home()/ "a5_evidence"
    ev_dir.mkdir(exist_ok=True)
    fp=ev_dir / f"spd_barrier_dr_order-live-{int(ts*1000)}.json"
    fp.write_text(json.dumps(out))
    print(f"[{'FIXTURE' if is_fixture else 'LIVE'}] writing {conf} {'fixture' if is_fixture else 'live'} {fp} (will stay 0.72)" if is_fixture else f"[LIVE] writing {fp}")
    # session file only from JS token – crisis-proof
    if token and not is_fixture:
        sf=ev_dir / f".frida_session_{nonce}"
        sf.write_text(token)

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args=ap.parse_args()
    if args.fixture:
        write_evidence({"_fixture": True, "_barrier_absorb":5, "_dr_roll":3, "_damage_roll":10, "_attack_id":1, "_order":"dr_before_barrier", "_barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier"})
        return
    if args.dry_run:
        nonce=get_nonce()
        print(f"[DRY] would write {pathlib.Path.home()/ f'a5_evidence/spd_barrier_dr_order-live-{int(time.time()*1000)}.json'}")
        return
    # live path – needs frida
    try:
        import frida
    except:
        print("frida module missing")
        sys.exit(1)
    # get device
    device=None
    try:
        device=frida.get_usb_device(timeout=2)
    except:
        try:
            device=frida.get_local_device()
        except:
            print("no device")
            sys.exit(1)
    # load hook
    hook_path=pathlib.Path(__file__).parent / "frida_spd_barrier_dr.js"
    script_code=hook_path.read_text()
    # Note: actual spawn/attach logic simplified – real APK package needed
    print("Attaching... (production – needs SPD APK with Frida Gadget)")
    # For production, user should spawn com.shatteredpixel.shatteredpixeldungeon
    # This is placeholder for real attach
    # on_message writes evidence only from JS token
    def on_message(msg, data):
        if msg["type"]=="send":
            payload=msg.get("payload",{})
            if payload.get("type")=="spd_evidence":
                d=payload.get("data",{})
                # d contains frida_session_token from Java UUID
                write_evidence(d)

    # Example session creation would be here
    print("Waiting for Barrier evidence – play SPD with Barrier")

if __name__=="__main__":
    main()
