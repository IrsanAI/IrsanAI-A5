# IrsanAI-A5 – Production Ready

**Torwart v3.3 crisis-proof – 0.72 SECURE AWAITING LIVE ATTESTATION / 0.88 ATTESTED**

- Guard zählt nur echte korrelierte Evidence: provider=a3_frida, target=spd, finding_id=spd_barrier_dr_order, observed Barrier+dr+attack_id, binary_sha256 APK-first streaming, device_id exact, frida_version exact, live_nonce + frida_session_token (Java UUID) + .frida_session_<nonce> + mtime±2s + age<30s + source=frida_js
- Handgeschriebene JSON selbst mit korrektem Nonce+Hash+Device+Frida → count=0 (FS attacker blocked)
- Runner: USB/Local Device, spawn/attach, Hook v3.3 java.util.UUID → send(spd_evidence)
- Cockpit: Production HUD, bind 0.0.0.0, zeigt warum 0.72

Tests: 6/6 grün – `aap_check.sh`
