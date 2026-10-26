import frida, json, pathlib, time, os, sys
target=os.path.expanduser("~/a5_targets/a5_crackme_v2")
ev_dir=pathlib.Path.home()/ "a5_evidence"
ev_dir.mkdir(exist_ok=True)
js=pathlib.Path("providers/frida_a5crackme2.js").read_text()

def get_device():
    # Frida 17: get_device_manager().local_device
    try:
        dm=frida.get_device_manager()
        return dm.local_device
    except AttributeError:
        pass
    try:
        return frida.get_local_device()
    except AttributeError:
        pass
    # fallback enumerate
    devs=frida.enumerate_devices()
    for d in devs:
        if d.type=='local' or 'local' in d.id.lower():
            return d
    return devs[0]

def on_msg(m,p):
    if m['type']=='send':
        pl=m.get('payload',{})
        if pl.get('type')=='observed':
            print(f"[+] REAL OBSERVED:",pl)
            ev={
              "evidence_id": f"a3-live-{int(time.time()*1000)}",
              "provider":"a3_frida",
              "target":"a5_crackme_v2",
              "confidence":"observed",
              "observed": pl,
              "method":"frida non-root local spawn",
              "ts": time.time()
            }
            path=ev_dir/f"a3_live_{int(time.time()*1000)}.json"
            path.write_text(json.dumps(ev,indent=2))
            print(f"[+] wrote {path} -> HONEST observed")

dev=get_device()
print(f"[*] device {dev.id} {dev.name} type={dev.type}")
print(f"[*] spawning {target} with key A5-Pro-Cockpit-2026!")
pid=dev.spawn([target, "A5-Pro-Cockpit-2026!"])
print(f"[*] pid {pid}")
sess=dev.attach(pid)
script=sess.create_script(js)
script.on('message', on_msg)
script.load()
dev.resume(pid)
print("[*] resumed, waiting 5s for hooks...")
time.sleep(5)
print("[*] done")
print("[*] evidence now:", list(ev_dir.glob("a3_live*.json")))
