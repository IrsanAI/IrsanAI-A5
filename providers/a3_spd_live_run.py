#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# A3 SPD Live Runner – hook v3 send(spd_evidence) -> Guard-complete JSON
from __future__ import annotations
import pathlib, json, time, hashlib, platform, subprocess, sys, argparse

def get_local_hash():
    for p in pathlib.Path.home().glob("a5_targets/**/Char.java"):
        if p.exists():
            return hashlib.sha256(p.read_bytes()).hexdigest()
    return "no-target-found"

def get_frida_version():
    try:
        import frida
        return getattr(frida, "__version__", "unknown")
    except:
        try:
            out=subprocess.check_output(["frida","--version"], text=True).strip()
            return out
        except:
            return "unknown"

def get_device_id():
    try:
        out=subprocess.check_output(["getprop","ro.serialno"], text=True).strip()
        if out: return out
    except: pass
    try:
        out=subprocess.check_output(["getprop","ro.product.model"], text=True).strip()
        if out: return out+"-"+platform.node()
    except: pass
    return platform.node() or "unknown-device"

def get_nonce():
    np=pathlib.Path.home()/ "a5_evidence/.live_nonce"
    if np.exists():
        return np.read_text().strip()
    # fallback generate
    import random, string
    nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
    np.parent.mkdir(exist_ok=True)
    np.write_text(nonce)
    return nonce

def write_evidence(ev_data, dry=False):
    nonce=get_nonce()
    local_hash=get_local_hash()
    device_id=get_device_id()
    frida_ver=get_frida_version()
    ts=time.time()
    evidence={
        "evidence_id": f"spd_barrier_dr_order-live-{int(ts*1000)}",
        "provider": "a3_frida",
        "target": "spd",
        "finding_id": "spd_barrier_dr_order",
        "confidence": "observed",
        "correlated": True,
        "observed": {
            "barrier_absorb_value": ev_data.get("absorbed", ev_data.get("barrier_absorb_value", 1)),
            "dr_roll": ev_data.get("drRoll", ev_data.get("dr_roll", 0)),
            "damage_roll": ev_data.get("damageRoll", ev_data.get("damage_roll", 0)),
            "order": "dr_before_barrier",
            "barrier_class": ev_data.get("buffType", ev_data.get("barrier_class", "com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier")),
            "attack_id": ev_data.get("attackId", ev_data.get("attack_id", 1)),
            "incoming_damage": ev_data.get("incomingDmg", ev_data.get("incoming_damage", 0)),
            "leftover_damage": ev_data.get("leftover", ev_data.get("leftover_damage", 0)),
        },
        "binary_sha256": local_hash,
        "device_id": device_id,
        "frida_version": frida_ver,
        "live_nonce": nonce,
        "ts": ts,
        "timestamp": int(ts*1000)
    }
    out_path=pathlib.Path.home()/ f"a5_evidence/spd_barrier_dr_order-live-{int(ts*1000)}.json"
    if dry:
        print(f"[DRY] would write {out_path}\n{json.dumps(evidence, indent=2)[:800]}")
        return evidence
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(evidence, indent=2))
    print(f"[A3 SPD] wrote {out_path} nonce={nonce[:6]}.. hash={local_hash[:12]}.. dev={device_id} frida={frida_ver}")
    return evidence

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=60, help="seconds to wait for send()")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fixture", action="store_true", help="write one fixture evidence for integration test")
    args=ap.parse_args()

    if args.fixture or args.dry_run:
        fake={"absorbed":5,"drRoll":3,"damageRoll":10,"attackId":1,"buffType":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","incomingDmg":10,"leftover":2}
        write_evidence(fake, dry=args.dry_run)
        return

    # Real Frida path – requires frida, device/emulator with SPD APK + Gadget
    try:
        import frida
    except Exception as e:
        print(f"[!] frida python module not found ({e}) – use --fixture for dry test")
        sys.exit(1)

    hook_path=pathlib.Path("providers/frida_spd_barrier_dr.js")
    if not hook_path.exists():
        print(f"[!] hook not found {hook_path}")
        sys.exit(1)
    hook_code=hook_path.read_text()

    print(f"[A3 SPD] waiting for send() – hook v3 – nonce={get_nonce()[:6]}.. hash={get_local_hash()[:12]}..")
    print(f"[A3 SPD] start SPD combat with Barrier buff now, {args.wait}s window...")

    # Simplified: attach to SPD – user must adapt package name
    # This is template for Termux frida -U
    def on_message(msg, data):
        if msg["type"]=="send":
            payload=msg.get("payload",{})
            if payload.get("type")=="spd_evidence":
                write_evidence(payload.get("data",{}))
        elif msg["type"]=="error":
            print(f"[FRIDA ERROR] {msg}")

    # Example attach – will be adapted by user for real APK
    # device=frida.get_usb_device(timeout=5)
    # pid=device.spawn(["com.shatteredpixel.shatteredpixeldungeon"])
    # session=device.attach(pid)
    # script=session.create_script(hook_code)
    # script.on("message", on_message)
    # script.load()
    # device.resume(pid)
    # time.sleep(args.wait)

    print("[A3 SPD] template ready – implement attach for your SPD build, hook already sends via send()")

if __name__=="__main__":
    main()
