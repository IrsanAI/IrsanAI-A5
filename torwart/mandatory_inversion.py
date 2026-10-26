#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import json, argparse, pathlib
from datetime import datetime, timezone

@dataclass
class RivalExplanation:
    text: str
    changes_diagnosis: bool = True

@dataclass
class AAPResult:
    phase0_intent: str
    phase0_access_limitations: str
    phase0_residual_uncertainty: str
    phase1_incident: str
    phase1_patterns: List[str]
    phase1_architecture: str
    phase1_higher_order_cause: str
    phase1_rivals: List[RivalExplanation]
    phase1_levers: List[str]
    phase1_strategy: str
    phase2_inversion: str
    phase3_survived: List[str]
    phase3_weakened: List[str]
    phase3_killed: List[str]
    phase3_shifted: List[str]
    phase4_changeable: List[str]
    phase4_resistant: List[str]
    phase4_residual_levers: List[str]
    stress_tested_diagnosis: str
    survival_assessment: str
    residual: str
    overall_confidence: float
    boundary_map: Dict[str, Any]
    method_note: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self):
        d=asdict(self); d["phase1_rivals"]=[asdict(r) for r in self.phase1_rivals]; return d
    def to_json(self, indent=2): return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

def count_real_observed(finding_id: str = "spd_barrier_dr_order") -> int:
    # FINAL HONEST: SPD-Live-Verifikation noch nicht implementiert
    # Gibt immer 0 zurück, egal welche JSON im Evidence-Verzeichnis liegt
    # 0.88 erfordert echten SPD Frida-Lauf mit korrelierten Barrier+DR Beobachtungen
    return 0

def check_closure_allowed(r: AAPResult):
    if r.overall_confidence > 0.8:
        # 0.88 darf nur mit echtem SPD Live kommen – aktuell nicht vorhanden
        if "spd" in r.phase0_intent.lower() and "not implemented" in r.phase0_access_limitations.lower():
            raise Exception("Closure blocked: SPD live not implemented cannot be 0.88")
    if r.phase0_residual_uncertainty=="high" and r.overall_confidence>0.7:
        raise Exception("Closure blocked: high residual must be <=0.7")
    return True

def run_spd_barrier_dr_residual():
    return AAPResult(
        "SPD Barrier vs DR – SPD-Live-Verifikation noch nicht implementiert",
        "SPD-Live-Verifikation noch nicht implementiert – kein SPD Build in ~/a5_targets/spd, kein korrelierter Frida Hook für Barrier.absorb+DR – 0.88 intentionally unreachable – fail-closed",
        "medium",
        "Static: Barrier.absorb then Normal(DRMin,DRMax) – needs live verification",
        ["Barrier Buff absorb","DR Normal roll","Glyph wrap"],
        "MeleeWeapon.damageRoll -> Barrier.absorb -> Normal(DRMin,DRMax) -> Glyph – unverified live order",
        "Barrier first (static hypothesis)",
        [RivalExplanation("order irrelevant",True), RivalExplanation("glyph re-introduces",True)],
        ["Build SPD in ~/a5_targets/spd","Implement Frida hook with stored overload (no recursion) for damageRoll+Barrier.absorb+DR","Verifier with 4 tests"],
        "Keep 0.72 until real SPD Frida live with correlated observations",
        "Barrier NOT before DR – would need live proof",
        ["Raw roll formula intact"],["Confidence medium – needs live"],[],["Need SPD runtime with Frida"],
        ["Build SPD","Real Frida hook"],["Source fixed upstream"],
        ["Frida SPD hook – must capture Barrier.absorb value AND DR range in SAME call"],
        "Static hypothesis – 0.72 – 0.88 requires real SPD Frida run",
        "partially reframed",
        "SPD-Live-Verifikation noch nicht implementiert – static only – 0.72 – 0.88 requires real SPD build + Frida run with correlated Barrier+DR observations",
        0.72,
        {"changeable":["Build SPD + implement correct overload hook"]},
        "AAP v1.2 FINAL HONEST – SPD live not implemented – fail-closed 0.72"
    )

def run_spd_barrier_dr_residual_i3(live_observations: int = 0):
    FINDING="spd_barrier_dr_order"
    real = count_real_observed(FINDING)
    base = run_spd_barrier_dr_residual()
    if live_observations>0:
        print(f"[!] Torwart FINAL: --live {live_observations} für {FINDING} – SPD-Live-Verifikation noch nicht implementiert (kein SPD Build, kein korrelierter Barrier+DR Hook) – real={real} – bleibe bei 0.72")
    base.phase0_intent=f"i3 FINAL – {FINDING} – SPD-Live-Verifikation noch nicht implementiert – live requested {live_observations} real={real}"
    base.overall_confidence=0.72; base.survival_assessment="partially reframed"
    check_closure_allowed(base); return base

def main():
    p=argparse.ArgumentParser(); p.add_argument("--i3",action="store_true"); p.add_argument("--live",type=int,default=0); a=p.parse_args()
    if a.i3:
        r=run_spd_barrier_dr_residual_i3(a.live)
        print(f"=== Torwart FINAL – SPD-Live NOT IMPLEMENTED – i3 live={a.live} real={count_real_observed()} ===\n")
    else:
        r=run_spd_barrier_dr_residual()
    print(r.to_json()); print(f"\n--- {r.survival_assessment} {r.overall_confidence} ---\n{r.residual}")

if __name__=="__main__": main()
