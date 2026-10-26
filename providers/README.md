# A3 SPD Live – Fail-Closed

**Status:** 0.72 fail-closed, Cockpit Demo/inferred bis echter Device-Run.

## Warum 0.72?
Guard `torwart/mandatory_inversion.py` zählt nur echte korrelierte Evidence:
- provider=a3_frida, target=spd, finding_id=spd_barrier_dr_order
- confidence=observed, correlated=true, fixture!=true
- observed.barrier_absorb_value + dr_roll + attack_id + order=dr_before_barrier + Barrier-only
- binary_sha256 = APK-Hash bevorzugt (wie Runner), sonst Char.java 8d372e8e...
- device_id == get_expected_device_id() (nicht localhost), frida_version == echt (nicht unknown)
- live_nonce + frida_session_token + .frida_session_<nonce> File mit gleichem Token (nur echter Frida on_message schreibt es)

Handgeschriebene JSON selbst mit korrektem Nonce+Hash+Device+Frida -> 0 ohne Session-File -> 0.72.

## Runner
- `python providers/a3_spd_live_run.py --dry-run` -> schreibt inferred Demo, zählt 0
- `python providers/a3_spd_live_run.py --fixture` -> schreibt inferred + fixture:true, zählt 0 (Demo-Schleife geblockt)
- Live: braucht USB/Local Device mit Frida: spawn/attach -> ShieldBuff.absorbDamage -> drRoll vor damageRoll -> send({type:spd_evidence})

## Cockpit
Server bindet 127.0.0.1, schreibt immer inferred demo-only bis Guard 0.88 liefert.

## Tests (müssen alle grün)
- test_torwart_strict.py (4)
- test_torwart_fake_full.py
- test_torwart_fake_correct_hash_no_nonce.py
- test_torwart_fake_full_handwritten_with_nonce.py (Manus final edge)
