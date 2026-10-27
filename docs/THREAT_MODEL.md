
# THREAT_MODEL.md – IrsanAI-A5 Torwart v4.3

## Ziel
`spd_barrier_dr_order` darf nur auf 0.88 gehen, wenn wirklich live Frida + echtes SPD APK + Barrier-Kampf beobachtet wurde.

## Annahmen
- Angreifer hat FS-Zugriff auf `~/a5_evidence/`
- Angreifer kann `touch -t`, JSON schreiben, mtimes fälschen

## Was geschützt wird

| Gegner | Geschützt? | Wie |
|--------|------------|-----|
| Offline-Fälschung (JSON mit korrektem Hash/Nonce) | JA | count=0 – erfordert live Frida, Java UUID, HMAC, private app dir |
| Anderer Android-User (andere UID) | JA | /data/data/.../files nicht lesbar für andere UID |
| Same-UID Angreifer (anderer Termux Prozess) | NEIN – out-of-scope | Same UID kann ~/.runner_secret lesen – dokumentiert, kein Overclaim |
| mtime-Touch | NEIN – mtime kein Security Boundary | Echter Schutz ist HMAC + Java UUID – mtime nur ordering, fail-closed |

## Non-forgeable – korrekt geframed
Non-forgeable against **offline / FS forgery of spd_barrier_dr_order → 0.88** under this doc: attacker = Termux shell without control of live SPD process and without real Frida session that produces Java-UUID tokens + runner HMAC.

Nicht absolut: "Niemand kann jemals 0.88 fälschen" – Root / kompromittierter SPD Prozess = out-of-scope.

## HMAC
Canonical form: `f"{token}|{nonce}|{attack_id}"` – delimiter prevents concatenation ambiguity, verified with `hmac.compare_digest` (constant-time), logs never leak expected value.
