#!/bin/bash
set -e
cd ~/irsanai
echo "=== AAP Check Production v4.0 – Non-Forgeable ==="
rm ~/a5_evidence/.live_nonce ~/a5_evidence/spd_barrier*.json ~/a5_evidence/.frida_session_* ~/a5_evidence/fake_*.json ~/a5_evidence/.runner_secret 2>/dev/null || true
PYTHONPATH=. python3 tests/test_torwart_strict.py
PYTHONPATH=. python3 tests/test_torwart_fake_full.py
PYTHONPATH=. python3 tests/test_torwart_fake_correct_hash_no_nonce.py
PYTHONPATH=. python3 tests/test_torwart_fake_full_handwritten_with_nonce.py
PYTHONPATH=. python3 tests/test_integration_fixture_must_not_unlock.py
# v4.0 FS forgery: source=frida_js with self-made session + token must be 0
PYTHONPATH=. python3 - << 'PY'
import pathlib, json, time, uuid, hashlib, hmac, os
from torwart.mandatory_inversion import count_real_observed, get_live_nonce_path, get_local_target_hash, get_expected_device_id, get_local_frida_version, is_frida_live
ev_dir=pathlib.Path.home()/ "a5_evidence"
ev_dir.mkdir(exist_ok=True)
import random, string
nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
get_live_nonce_path().parent.mkdir(exist_ok=True)
get_live_nonce_path().write_text(nonce)
token=str(uuid.uuid4())
(ev_dir/ f".frida_session_{nonce}").write_text(token)
fake=ev_dir/ f"spd_barrier_dr_order-live-{int(time.time()*1000)}.json"
fake.write_text(json.dumps({
 "finding_id":"spd_barrier_dr_order","provider":"a3_frida","target":"spd","confidence":"observed","correlated":True,
 "observed":{"barrier_absorb_value":5,"dr_roll":3,"damage_roll":10,"order":"dr_before_barrier","barrier_class":"com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier","attack_id":1},
 "binary_sha256": get_local_target_hash(), "device_id": get_expected_device_id(), "frida_version": get_local_frida_version(),
 "live_nonce": nonce, "frida_session_token": token, "source": "frida_js", "java_uuid_source": "java.util.UUID", "ts": time.time()
}))
cnt=count_real_observed()
print(f"FS forgery source=frida_js self-made session count={cnt} expected 0")
assert cnt==0, f"FS forgery with source=frida_js must be 0 in v4.0, got {cnt}"
fake.unlink(); (ev_dir/ f".frida_session_{nonce}").unlink(missing_ok=True)
get_live_nonce_path().unlink(missing_ok=True)
print("PASS v4.0 FS forgery blocked – non-forgeable")
PY
echo "PRODUCTION READY v4.0 – 0.72 SECURE, FS forgery blocked, live Frida required for 0.88"
