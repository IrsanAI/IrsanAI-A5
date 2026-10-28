# SIGNING – IrsanAI-A5 Torwart – v4.3.6 (02490fb)

## Current Status
**PRODUCTION READY v4.3.6 – 0.72 SECURE – HMAC canonical fixed**
Commit: `02490fb` (HEAD main)
CI: AAP Check v4.3.3 #6 – Erfolg 15s – aap-check 11s – 02490fb main

## Badge
```markdown
[![Security Audit](https://img.shields.io/badge/security-audited%20v4.3.6-green.svg)](docs/THREAT_MODEL.md)
```

## Audit Trail

### v4.3.5 – Commit 5376c5a – Manus Fixes
- Manus audit d3efad5 found 2 critical: private token not mandatory, is_frida_live without SPD
- Fixed in 5376c5a: private token mandatory + is_frida_live requires SPD+token (different UID <30s)
- Audits:
  - Gemini 2.5 Pro 10:02 UTC – Non-forgeable Ja, Production Ready Ja, badge green v4.3.5
  - Grok 4.5 08:03 UTC – Non-forgeable Ja, Production Ready Ja, badge green v4.3.5
  - Perplexity 09:03 UTC – PASS code-level, Production Ready with Vorbehalt (no CI reproduction)
- CI: #4 14s green

### v4.3.6 – Commit fb7496b + 02490fb – HMAC Canonical Fix + aap_check clean
- GLM 5.3 Vibe audit at 5376c5a found F1 HIGH: HMAC canonical mismatch
  - Producer: `f"{token}{nonce}{attack_id}"` WITHOUT |
  - Verifier: `f"{token}|{nonce}|{attack_id}"` WITH |
  - Impact: 0.88 ATTESTED LIVE blocked by hmac invalid (fail-closed, no leak)
- Fix: fb7496b sets producer to `f"{token}|{nonce}|{attack_id}"` – matches THREAT_MODEL.md and verifier
- fb7496b had sed breaking heredoc line 22 '(' -> CI #5 13s red
- 02490fb restores clean aap_check.sh – CI #6 15s green, aap-check 11s success

#### Quad-Audit v4.3.6 (02490fb)
1. **Perplexity 09:32 UTC** – Statisch:
   - HMAC canonical: Producer f"{token}|{nonce}|{attack_id}" == Verifier canonical = f"{token}|{j.get('live_nonce')}|{obs.get('attack_id')}" + compare_digest – F1 GEFIXT
   - Manus fixes still present, no HMAC leak, no Frida subprocess
   - Verdict: Non-forgeable Ja, Production Ready Bedingt Ja – wanted CI log -> CI #6 green now provided -> upgrades to Ja
   - Badge: hold yellow until CI log (now green)

2. **Gemini 2.5 Pro 10:31 UTC** – 
   - All 11 criteria Ja, F1 fixed verified, aap_check clean
   - Verdict: Non-forgeable Ja, Production Ready Ja, Confidence 0.88/0.72, badge green v4.3.6

3. **GLM 5.3 Vibe (Mistral AI) – Blob-SHA verified**:
   - Commit chain verified 02490fb = HEAD, since 5376c5a exactly 2 commits (fb7496b, 02490fb) only affecting provider + aap_check
   - Blob-SHA: mandatory_inversion.py b5476d49... and spd.py 1ae1f99d... byte-identical to v4.3.5 – Manus fixes persist
   - Producer: providers/a3_spd_live_run.py:104 now `f"{token}|{nonce}|{attack_id}"` – F1 GEFIXT, 0.88 reachable code-side
   - Carry-over: F2 test coverage private token, F3 CI python mismatch, F4 cockpit HEAD, F5 runner subprocess fallback – non-critical
   - Verdict: Non-forgeable JA, Production Ready JA as 0.72 gate (0.88 code-consistent), badge green v4.3.6

4. **Grok 4.5**:
   - Producer f"{token}|{nonce}|{attack_id}" @104 matches verifier token|nonce|attack_id + compare_digest
   - Manus #1 private token mandatory ~300-310, #2 SPD+Token, no HMAC leak, no Frida subprocess, ALL 4 TESTS PASS, PRODUCTION READY v4.3.6
   - Verdict: Non-forgeable Ja, Production Ready Ja, Confidence 0.72/0.88 live, badge green v4.3.6

## CI History
- #2 fix(ci) v4.3.3 portable cd – 18s green – fixes cd ~/irsanai on ubuntu-latest
- #3 v4.3.4 avoid frida binary segfault – 16s green – import frida only
- #4 v4.3.5 Manus audit – 14s green – private token mandatory + is_frida_live SPD+Token
- #5 v4.3.6 HMAC canonical mismatch – 13s red – sed broke heredoc (fb7496b)
- #6 v4.3.6 aap_check clean – 15s green – aap-check 11s success – 02490fb HEAD (THIS)

## Security Guarantees v4.3.6
- Offline FS forgery without live signal blocked count=0
- HMAC canonical token|nonce|attack_id with | + compare_digest + no expected HMAC leak
- Frida binary subprocess avoided in verifier (import frida only) – avoids Termux ARM64 segfault 17.2.14
- is_frida_live requires SPD process found via is_target_process() AND private token .a5_frida_token_* with different UID and age <30s
- Private token mandatory for 0.88 (count_without_private_app_token=0)
- Rejections logged, fail-closed 0.72 always, 0.88 only with genuine live attestation

## Next
- 0.88 ATTESTED LIVE now code-consistent, requires real device demo (Frida + SPD + private token + HMAC) for final live proof
- Open low findings: F2 test coverage, F3 CI python 3.11 vs 3.12, F4 cockpit do_HEAD, F5 runner subprocess fallback – non-blocking for 0.72 gate

Signed: universal-auditor quad (Gemini 2.5 Pro, Grok 4.5, GLM 5.3 Vibe, Perplexity) – 2026-10-28 10:50 UTC – Commit 02490fb
