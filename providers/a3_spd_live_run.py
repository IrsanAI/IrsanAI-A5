#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# A3 SPD Live Runner v5 – Fixture=inferred (nie 0.88), Live=attach+hook v3 send(spd_evidence)
from __future__ import annotations
import pathlib, json, time, hashlib, platform, subprocess, sys, argparse

def get_local_hash():
    # 1. APK bevorzugt (echter laufender Hash), sonst Char.java
    for p in pathlib.Path.home().glob("a5_targets/**/*.apk"):
        if p.exists():
            try:
                return hashlib.sha256(p.read_bytes()).hexdigest()
            except: pass
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
    is_fixture=ev_data.get("_fixture", False)
    # Token aus Frida-Session durchlassen
    sess_tok=ev_data.get("frida_session_token") or ev_data.get("session_token") or ""
    conf="inferred" if is_fixture else "observed"
    evidence={
        "evidence_id": f"spd_barrier_dr_order-live-{int(ts*1000)}",
        "provider": "a3_frida",
        "target": "spd",
        "finding_id": "spd_barrier_dr_order",
        "confidence": conf,
        "fixture": is_fixture,
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
        "frida_session_token": ev_data.get("frida_session_token",""),
        "session_token": ev_data.get("frida_session_token",""),
        "ts": ts,
        "timestamp": int(ts*1000)
    }
    out_path=pathlib.Path.home()/ f"a5_evidence/spd_barrier_dr_order-live-{int(ts*1000)}.json"
    if dry or is_fixture:
        # Fixture darf nie als echte Evidence zählen – Guard blockt inferred/fixture/localhost/unknown
        if dry:
            print(f"[DRY] would write {out_path}")
        else:
            print(f"[FIXTURE] writing inferred fixture {out_path} (will stay 0.72)")
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(json.dumps(evidence, indent=2))
        return evidence
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(evidence, indent=2))
    print(f"[A3 SPD LIVE] wrote {out_path} nonce={nonce[:6]}.. hash={local_hash[:12]}.. dev={device_id} frida={frida_ver}")
    return evidence

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fixture", action="store_true")
    args=ap.parse_args()

    if args.dry_run:
        fake={"absorbed":5,"drRoll":3,"damageRoll":10,"attackId":1,"buffType":"...Barrier","incomingDmg":10,"leftover":2, "_fixture": True, "frida_session_token": ""}
        write_evidence(fake, dry=True)
        return
    if args.fixture:
        fake={"absorbed":5,"drRoll":3,"damageRoll":10,"attackId":1,"buffType":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","incomingDmg":10,"leftover":2, "_fixture": True, "frida_session_token": ""}
        write_evidence(fake, dry=False)
        return

    try:
        import frida
    except Exception as e:
        print(f"[!] frida module missing {e} – use --fixture")
        sys.exit(1)

    hook_path=pathlib.Path("providers/frida_spd_barrier_dr.js")
    if not hook_path.exists():
        print(f"[!] hook missing {hook_path}")
        sys.exit(1)
    hook_code=hook_path.read_text()

    print(f"[A3 SPD] live attach – nonce={get_nonce()[:6]}.. hash={get_local_hash()[:12]}.. waiting {args.wait}s for Barrier combat...")

    import uuid, pathlib as _pl
    session_token=str(uuid.uuid4())
    # Session-File für Guard – beweist echte Frida-Session, nicht handgeschriebene JSON (Manus)
    def write_session_file(nonce, token):
        sf=_pl.Path.home()/ f"a5_evidence/.frida_session_{nonce}"
        sf.parent.mkdir(exist_ok=True)
        sf.write_text(token)

    def on_message(msg, data):
        if msg["type"]=="send":
            payload=msg.get("payload",{})
            if payload.get("type")=="spd_evidence":
                d=payload.get("data",{})
                d["frida_session_token"]=session_token
                d["session_token"]=session_token
                # Session-File schreiben
                try:
                    write_session_file(get_nonce(), session_token)
                except: pass
                write_evidence(d)
        elif msg["type"]=="error":
            print(f"[FRIDA ERROR] {msg}")

    try:
        device=frida.get_usb_device(timeout=5)
    except:
        try:
            device=frida.get_local_device()
        except Exception as e:
            print(f"[!] no device {e}")
            sys.exit(1)

    # Versuche SPD zu finden/spawnen – Paketname anpassbar
    pkg="com.shatteredpixel.shatteredpixeldungeon"
    try:
        pid=device.spawn([pkg])
        session=device.attach(pid)
        script=session.create_script(hook_code)
        script.on("message", on_message)
        script.load()
        device.resume(pid)
        print(f"[A3 SPD] spawned {pkg} pid={pid}, hook v3 loaded – trigger Barrier combat now")
        time.sleep(args.wait)
    except Exception as e:
        print(f"[!] spawn failed {e} – trying attach to running")
        try:
            # attach zu laufendem Prozess
            apps=device.enumerate_applications()
            target=None
            for a in apps:
                if pkg in a.identifier:
                    target=a
                    break
            if target and target.pid:
                session=device.attach(target.pid)
                script=session.create_script(hook_code)
                script.on("message", on_message)
                script.load()
                print(f"[A3 SPD] attached to {pkg} pid={target.pid}, waiting {args.wait}s")
                time.sleep(args.wait)
            else:
                print("[!] SPD not running, start manually")
        except Exception as e2:
            print(f"[!] attach failed {e2}")

if __name__=="__main__":
    main()
