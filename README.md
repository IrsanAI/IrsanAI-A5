# IrsanAI-A5

**Agent-first Reverse Engineering Stack**  
A5 + AAP Torwart (Goalkeeper)

---

## Stack (verbindlich)

| Layer | Component | Role | License |
|-------|-----------|------|---------|
| **A1** | REA MCP + ReaGhidraBridge | Orchestration only (does **not** decompile itself). Headless bridge to Ghidra 12.1.x + JDK21 | MIT |
| **A2** | Ghidra headless | Decompilation / analysis engine | Apache 2.0 |
| **A3** | Frida / Qiling | Dynamic truth (Gadget non-root for Android) | wxWindows 3.1 / GPL-compatible |
| **A4** | capa + PCode / angr | Capability & symbolic analysis | Apache 2.0 / BSD-2-Clause |
| **A5** | Evidence-Graph + Verifier + **Torwart (AAP v1.2)** | Mandatory gate from medium confidence upward | Apache 2.0 |

**Torwart is non-negotiable** (see `torwart/mandatory_inversion.py` and `SYSTEM_PROMPT.md`): Best Diagnosis
→ Mandatory Inversion (hard counter-position)
→ Re-Synthesis
→ Survival Assessment
[largely survived | partially reframed | significantly reframed | largely collapsed]
→ Residual + Confidence update
→ only then Verifier / Closure  ---

## Baseline Targets (legal only)

1. **Shattered Pixel Dungeon** (GPLv3)  
   Formula proven, Verifier **5/5 PASS**  
   Static confidence 0.94–0.96 (high) / E2E 0.80 (medium)  
   Residual: Barrier vs. DR order

2. **checkme.c** (own 13-byte key `A5-CrackMe!!!`)  
   Existence high / Uniqueness low (unsigned char wrap)

---

## Quickstart (Termux-First)

```bash
# Clone
git clone https://github.com/IrsanAI/IrsanAI-A5.git
cd IrsanAI-A5

# Evidence directory (never hard-code long absolute paths)
EVIDENCE_DIR="${HOME}/a5_evidence"
[ -d "$EVIDENCE_DIR" ] || mkdir -p "$EVIDENCE_DIR"

# SPD CLI (expects local SPD checkout under \~/shattered-pixel-dungeon)
./cli/spd_cli.sh See cli/spd_cli.sh for Termux-safe patterns (find + [ -d ] || mkdir -p).
├── SYSTEM_PROMPT.md          # Canonical A5 + Torwart definition (kept in sync)
├── NOTICE                    # Third-party attribution (Ghidra, Frida, SPD, …)
├── LICENSE                   # Apache 2.0 (full text)
├── COLLABORATION.md          # Grok = Maintainer, Meta = Reviewer/Gatekeeper
├── REVIEWER_CHECKLIST.md     # Merge gates
├── docs/vision.md
├── evidence/schema.sql       # Evidence + Diagnosis tables
├── torwart/mandatory_inversion.py
├── cli/spd_cli.sh
└── providers/                # Stubs for A1 MCP Provider + A3 Frida Gadget
Collaboration Rules
Grok = Maintainer (code, CLIs, PRs, Termux readiness)
Meta = Reviewer + Gatekeeper
Merge only when:
evidence_id, file:line, offset, sha256, confidence (observed/inferred), limitation present
SHA256 over target artifacts
Torwart run with Survival Assessment
Verifier PASS
Termux-First patterns respected
See COLLABORATION.md and REVIEWER_CHECKLIST.md.
License & Attribution
Licensed under the Apache License 2.0.
Full text in LICENSE.
Third-party attributions and license notes in NOTICE.
No Ghidra, Frida or SPD source is redistributed.
Only legal targets are analysed.
