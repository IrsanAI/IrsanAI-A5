import pathlib, json, time, hashlib, os
from torwart.mandatory_inversion import count_real_observed, run_spd_barrier_dr_residual_i3, get_local_target_hash, get_local_frida_version

ev_dir=pathlib.Path.home()/ "a5_evidence"
ev_dir.mkdir(exist_ok=True)

# Manus Fake: alle Felder, 64-char SHA random, plausible device-id, aktueller ts, ohne local hash + ohne nonce
fake_path=ev_dir/"fake_full_64char.json"
fake={
  "evidence_id":"spd_barrier_dr_order-live-fake-full",
  "provider":"a3_frida",
  "target":"spd",
  "finding_id":"spd_barrier_dr_order",
  "confidence":"observed",
  "correlated":True,
  "observed":{
    "barrier_absorb_value":5,
    "dr_roll":3,
    "dr_min":3,
    "dr_max":3,
    "damage_roll":10,
    "incoming_damage":10,
    "leftover_damage":2,
    "order":"dr_before_barrier",
    "barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier",
    "attack_id":1
  },
  "binary_sha256": hashlib.sha256(os.urandom(32)).hexdigest(),  # random 64-char, nicht local hash
  "device_id":"real-device-12345",
  "frida_version": get_local_frida_version(),
  "timestamp": int(time.time()*1000),
  "ts": time.time()
}
fake_path.write_text(json.dumps(fake))

cnt=count_real_observed("spd_barrier_dr_order")
print(f"Fake full random SHA count={cnt} (expected 0)")
assert cnt==0, f"Fully filled fake with random SHA must be 0, got {cnt}"

r=run_spd_barrier_dr_residual_i3(1)
print(f"After fake full, live 1 -> conf={r.overall_confidence} expected 0.72")
assert r.overall_confidence==0.72, f"Fake full must stay 0.72, got {r.overall_confidence}"

fake_path.unlink()
# cleanup nonce
nonce_path=pathlib.Path.home()/ "a5_evidence/.live_nonce"
if nonce_path.exists(): nonce_path.unlink()

print("PASS fake full 64-char SHA -> stays 0.72 (Manus regression fixed)")
