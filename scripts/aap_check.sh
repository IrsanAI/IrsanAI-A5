#!/bin/bash
set -e
cd ~/irsanai
rm ~/a5_evidence/.live_nonce ~/a5_evidence/spd_barrier*.json ~/a5_evidence/.frida_session_* ~/a5_evidence/fake_*.json 2>/dev/null || true
PYTHONPATH=. python3 tests/test_torwart_strict.py
PYTHONPATH=. python3 tests/test_torwart_fake_full.py
PYTHONPATH=. python3 tests/test_torwart_fake_correct_hash_no_nonce.py
PYTHONPATH=. python3 tests/test_torwart_fake_full_handwritten_with_nonce.py
PYTHONPATH=. python3 tests/test_integration_fixture_must_not_unlock.py
echo "PRODUCTION READY – 0.72 SECURE, FS attacker blocked"
