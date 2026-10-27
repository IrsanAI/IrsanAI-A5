# ARCHITECTURE.md v4.3

## Quickstart
git clone https://github.com/IrsanAI/IrsanAI-A5
cd IrsanAI-A5
pip install frida-tools
./scripts/aap_check.sh  # muss 0.72 bleiben, zeigt rejections mit Grund
python providers/a3_spd_live_run.py  # echtes Device nötig für 0.88

## Diagramm
[SPD APK] -> [Frida Hook frida_spd_barrier_dr.js] - Java UUID.randomUUID() im Zielprozess
-> [Live Runner a3_spd_live_run.py] schreibt .live_nonce + .frida_session_<nonce> raw token + .runner_secret
-> [a5_evidence/*.json source=frida_js]
-> [Torwart Core generic + targets/spd.py Plugin (PROCESS_KEYWORDS, TARGET_NAME, is_target_process)]
-> 0.72 SECURE AWAITING LIVE ATTESTATION / 0.88 ATTESTED LIVE

## Modularisierung v4.3
Core: generic – nonce, session raw, hmac constant-time (compare_digest), canonical f"{token}|{nonce}|{attack_id}", device, frida version, no HMAC prefix in logs
Plugin: torwart/targets/spd.py – PROCESS_KEYWORDS, TARGET_NAME, is_target_process(), is_valid_target_file(), validate_observed()

## Cockpit v4.3
server.py default 127.0.0.1, 0.0.0.0 nur mit --token via X-A5-Token header (nicht query), serves fixed dist dir, no dead code
