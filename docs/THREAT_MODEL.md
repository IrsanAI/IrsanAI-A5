# THREAT_MODEL.md – IrsanAI-A5 Torwart v4.2

## Ziel
spd_barrier_dr_order darf nur auf 0.88 gehen, wenn wirklich live Frida + echtes SPD APK + Barrier-Kampf beobachtet wurde.

## Annahmen
- Angreifer hat FS-Zugriff auf ~/a5_evidence/
- Angreifer kann touch -t, JSON schreiben, mtimes fälschen

## Was geschützt wird

| Gegner | Geschützt? | Wie |
| Offline-Fälschung (JSON mit korrektem Hash/Nonce) | JA | count=0 – erfordert live Frida, Java UUID, HMAC, private app dir |
| Anderer Android-User (andere UID) | JA | /data/data/.../files nicht lesbar für andere UID |
| Same-UID Angreifer (anderer Termux Prozess) | NEIN – out-of-scope | Same UID kann ~/.runner_secret lesen – dokumentiert, kein Overclaim |
| mtime-Touch | NEIN – mtime kein Security Boundary | Echter Schutz ist HMAC mit Runner-Secret + Java UUID |

## Non-forgeable = HMAC + Java UUID + private App Dir, nicht mtime ±2s
