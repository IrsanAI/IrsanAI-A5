import pathlib, json, time
from torwart.mandatory_inversion import count_real_observed, get_local_target_hash, get_local_frida_version
ev_dir=pathlib.Path.home()/ "a5_evidence"; ev_dir.mkdir(exist_ok=True)
# cleanup
for f in ev_dir.glob("fake_*.json"): f.unlink(missing_ok=True)
fake=ev_dir/"fake_correct_hash_no_nonce.json"
fake.write_text(json.dumps({
  "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":"observed","correlated":True,
  "observed":{"barrier_absorb_value":5,"dr_roll":3,"damage_roll":10,"order":"dr_before_barrier","barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","attack_id":1},
  "binary_sha256": get_local_target_hash(),
  "device_id":"real-device-12345","frida_version":get_local_frida_version(),"ts":time.time()
}))
cnt=count_real_observed()
print(f"correct hash no nonce count={cnt} expected 0")
assert cnt==0, f"must be 0 without nonce, got {cnt}"
fake.unlink()
print("PASS correct hash without nonce -> 0 (Manus edge fixed)")
