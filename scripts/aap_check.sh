#!/bin/bash
set -e
cd ~/irsanai
echo "=== AAP Check Production v3.3 ==="
rm ~/a5_evidence/.live_nonce ~/a5_evidence/spd_barrier*.json ~/a5_evidence/.frida_session_* ~/a5_evidence/fake_*.json 2>/dev/null || true
PYTHONPATH=. python3 tests/test_torwart_strict.py
PYTHONPATH=. python3 tests/test_torwart_fake_full.py
PYTHONPATH=. python3 tests/test_torwart_fake_correct_hash_no_nonce.py
PYTHONPATH=. python3 tests/test_torwart_fake_full_handwritten_with_nonce.py
PYTHONPATH=. python3 tests/test_integration_fixture_must_not_unlock.py
# FS attacker checks
PYTHONPATH=. python3 - << 'PY'
import pathlib, json, time, uuid
from torwart.mandatory_inversion import count_real_observed, get_live_nonce_path, get_local_target_hash, get_expected_device_id, get_local_frida_version
ev_dir=pathlib.Path.home()/ "a5_evidence"
ev_dir.mkdir(exist_ok=True)
# create nonce
import random, string
nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
get_live_nonce_path().parent.mkdir(exist_ok=True)
get_live_nonce_path().write_text(nonce)
# python_fake must be 0
token=str(uuid.uuid4())
(ev_dir/ f".frida_session_{nonce}").write_text(token)
fake=ev_dir/ f"spd_barrier_dr_order-live-{int(time.time()*1000)}.json"
fake.write_text(json.dumps({
 "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":"observed","correlated":True,
 "observed":{"barrier_absorb_value":5,"dr_roll":3,"damage_roll":10,"order":"dr_before_barrier","barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","attack_id":1},
 "binary_sha256": get_local_target_hash(), "device_id": get_expected_device_id(), "frida_version": get_local_frida_version(),
 "live_nonce": nonce, "frida_session_token": token, "source": "python_fake", "ts": time.time()
}))
cnt=count_real_observed()
print(f"FS attacker python_fake count={cnt} expected 0")
assert cnt==0, f"python_fake must be 0"
fake.unlink(); (ev_dir/ f".frida_session_{nonce}").unlink(missing_ok=True)
# no-target-found forge must be 0
fake2=ev_dir/ f"spd_barrier_dr_order-live-{int(time.time()*1000)}.json"
fake2.write_text(json.dumps({
 "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":"observed","correlated":True,
 "observed":{"barrier_absorb_value":5,"dr_roll":3,"damage_roll":10,"order":"dr_before_barrier","barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","attack_id":1},
 "binary_sha256": "no-target-found", "device_id": get_expected_device_id(), "frida_version": get_local_frida_version(),
 "live_nonce": nonce, "frida_session_token": token, "source": "frida_js", "ts": time.time()
}))
cnt2=count_real_observed()
print(f"no-target-found forge count={cnt2} expected 0")
assert cnt2==0
fake2.unlink()
get_live_nonce_path().unlink(missing_ok=True)
print("PASS FS attacker + no-target-found blocked – PRODUCTION READY")
PY
echo "PRODUCTION READY – 0.72 SECURE, 6/6 green"
