# ARCHITECTURE.md v4.2

## Quickstart
git clone https://github.com/IrsanAI/IrsanAI-A5
cd IrsanAI-A5
pip install frida-tools
./scripts/aap_check.sh  # muss 0.72 bleiben
python providers/a3_spd_live_run.py  # echtes Device nötig für 0.88

## Diagramm
[SPD APK] -> [Frida Hook] - Java UUID -> [Live Runner] -> [a5_evidence/*.json source=frida_js]
-> [Torwart Core generic + targets/spd.py Plugin] -> 0.72 / 0.88

## Modular
Core: generic – nonce, session raw token, hmac, device, frida version
Plugin: torwart/targets/spd.py – nur SPD

## Cockpit Fix
server.py default 127.0.0.1, 0.0.0.0 nur mit --token
