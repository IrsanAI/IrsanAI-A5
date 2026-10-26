import pathlib, json, time
from torwart.mandatory_inversion import count_real_observed, get_local_target_hash, get_local_frida_version, get_expected_device_id, get_live_nonce_path
ev_dir=pathlib.Path.home()/ "a5_evidence"; ev_dir.mkdir(exist_ok=True)
# cleanup
for f in ev_dir.glob("*.json"): f.unlink(missing_ok=True)
for f in ev_dir.glob(".frida_session_*"): f.unlink(missing_ok=True)
# Nonce wie echter Live-Lauf
import random, string
nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
get_live_nonce_path().parent.mkdir(exist_ok=True)
get_live_nonce_path().write_text(nonce)

# Handgeschriebene voll ausgefüllte JSON – wie Manus isolierter Test
fake=ev_dir/f"spd_barrier_dr_order-live-{int(time.time()*1000)}.json"
fake.write_text(json.dumps({
  "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":"observed","correlated":True,
  "observed":{"barrier_absorb_value":5,"dr_roll":3,"damage_roll":10,"order":"dr_before_barrier","barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","attack_id":1},
  "binary_sha256": get_local_target_hash(), # passend
  "device_id": get_expected_device_id(), # echt
  "frida_version": get_local_frida_version(), # echt
  "live_nonce": nonce, # aktuell
  "ts": time.time(),
  "timestamp": int(time.time()*1000)
  # KEIN frida_session_token + KEIN Session-File -> muss 0 bleiben
}))
cnt=count_real_observed()
print(f"handwritten full with nonce+hash count={cnt} expected 0")
assert cnt==0, f"handwritten with nonce+hash must be 0 without Frida session proof, got {cnt}"
fake.unlink()
get_live_nonce_path().unlink(missing_ok=True)
print("PASS handwritten full with nonce+hash -> 0 (Manus final regression fixed)")
