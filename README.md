# IrsanAI-A5 – PRODUCTION READY v4.3

**PRODUCTION READY v4.3 – 0.72 fail-closed**
**FS/offline forgery of 0.88 blocked (see docs/THREAT_MODEL.md)**
**0.88 only after live Frida attestation on legal SPD (GPLv3)**

## Was ist Torwart?
Mandatory Inversion Gate – Pflicht-Gegenposition ab medium Confidence, Re-Synthese, Survival Assessment gegen Bestätigungs-Bias.

## Quickstart
./scripts/aap_check.sh  # ALL 4 TESTS PASS, 0.72 SECURE, rejections logged

## Security
- v4.2: Grok Re-Audit – is_frida_live=False ohne SPD, count=0, FORGE FAILED
- v4.3: Le Chat fixes – HMAC leak removed (no expected prefix in log, compare_digest constant-time, canonical f"{token}|{nonce}|{attack_id}"), README synced to v4.3, target fully extracted, cockpit dead code removed
- See docs/THREAT_MODEL.md – Same-UID out-of-scope, mtime not security boundary

## Cockpit
python extensions/cockpit/server.py --host 127.0.0.1 --port 8000
For LAN: --host 0.0.0.0 --token <secret> --root ./extensions/cockpit/dist
Auth via X-A5-Token header (not query string)

## Architektur
See docs/ARCHITECTURE.md
