#!/usr/bin/env python3
"""
IrsanAI-A5 Torwart (Goalkeeper) – AAP v1.2 (Adversarial Ascent Protocol)
Mandatory from medium confidence upward. Non-negotiable gate.

Phases (canonical):
  0  Setup          – Intent, Access Limitations, Residual Uncertainty
  1  Root-Ascent    – Incident → Patterns → Architecture → Higher-Order Cause
                     + 2-4 Rival Explanations + Levers + Operational Strategy
  2  Mandatory Inversion – exact opposite of best diagnosis, treated as temporarily true
  3  Re-Synthesis   – what survived / weakened / killed / shifted
  4  Boundary Map   – changeable / systemically resistant / residual levers
  5  Final Output   – stress-tested diagnosis + Boundary Map + levers
                     + Method Note with Survival Assessment
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json
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

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["phase1_rivals"] = [asdict(r) for r in self.phase1_rivals]
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def run_aap_v1_2(
    intent: str,
    access_limitations: str,
    residual_uncertainty: str,
    incident: str,
    patterns: List[str],
    architecture: str,
    higher_order_cause: str,
    rivals: List[RivalExplanation],
    levers: List[str],
    strategy: str,
    best_diagnosis: str,
    hard_inversion: str,
) -> AAPResult:
    if residual_uncertainty not in ("low", "medium", "high"):
        raise ValueError("residual_uncertainty must be low|medium|high")

    inversion = hard_inversion.strip()
    if not inversion or inversion.lower() == best_diagnosis.lower():
        raise ValueError("Mandatory Inversion must be a hard, non-identical counter-position")

    return AAPResult(
        phase0_intent=intent,
        phase0_access_limitations=access_limitations,
        phase0_residual_uncertainty=residual_uncertainty,
        phase1_incident=incident,
        phase1_patterns=patterns,
        phase1_architecture=architecture,
        phase1_higher_order_cause=higher_order_cause,
        phase1_rivals=rivals,
        phase1_levers=levers,
        phase1_strategy=strategy,
        phase2_inversion=inversion,
        phase3_survived=[],
        phase3_weakened=[],
        phase3_killed=[],
        phase3_shifted=[],
        phase4_changeable=[],
        phase4_resistant=[],
        phase4_residual_levers=[],
        stress_tested_diagnosis=best_diagnosis,
        survival_assessment="largely survived",
        residual="",
        overall_confidence=0.5,
        boundary_map={},
        method_note="AAP v1.2 generic skeleton – override in concrete target run",
    )


def check_closure_allowed(result: AAPResult) -> bool:
    if not result.survival_assessment:
        raise Exception("Closure blocked: missing Survival Assessment")
    if result.survival_assessment not in (
        "largely survived",
        "partially reframed",
        "significantly reframed",
        "largely collapsed",
    ):
        raise Exception(f"Closure blocked: invalid survival value '{result.survival_assessment}'")
    if result.phase0_residual_uncertainty == "high" and result.overall_confidence > 0.7:
        raise Exception("Closure blocked: high residual uncertainty forces cautious confidence")
    return True


def run_spd_barrier_dr_residual() -> AAPResult:
    intent = (
        "Close the residual uncertainty about the relative order of "
        "Barrier.absorb() versus DR (armor) subtraction in the SPD melee damage path."
    )
    access = (
        "Static source only (MeleeWeapon.java + related Glyph/Buff classes). "
        "No runtime instrumentation in this run. Termux-First, legal GPLv3 target."
    )
    uncertainty = "medium"

    incident = (
        "Static reading yields: buffed damage is first reduced by Barrier.absorb, "
        "then by a Normal(DRMin, DRMax) roll. Residual: order may invert under "
        "certain glyph or buff combinations."
    )
    patterns = [
        "Barrier is a Buff that absorbs a fixed amount before further mitigation",
        "DR is rolled per hit (Normal distribution between DRMin and DRMax)",
        "Glyphs can wrap the final effective value",
        "Augment DAMAGE 1.5 / SPEED 0.7 multiplies the raw roll",
    ]
    architecture = (
        "MeleeWeapon.damageRoll → raw = NormalIntRange(min,max)*aug + Uniform(0,exStr); "
        "then Barrier.absorb(buffed); then subtract Normal(DRMin,DRMax); finally Glyph."
    )
    higher_cause = (
        "Design intent appears to be 'Barrier first, then armor DR', "
        "so that absorption is predictable and independent of the DR roll."
    )
    rivals = [
        RivalExplanation(
            "Barrier and DR are commutative under all current glyphs – order is irrelevant",
            changes_diagnosis=True,
        ),
        RivalExplanation(
            "Some glyphs (e.g. anti-magic / conditional) apply after DR and can "
            "re-introduce damage that Barrier already absorbed, effectively inverting order",
            changes_diagnosis=True,
        ),
        RivalExplanation(
            "Overflow formula on DRMax (tier*(2+lvl) + ((lvl-max)+1)/2) can make DR larger "
            "than Barrier capacity, masking any order effect in high-level play",
            changes_diagnosis=False,
        ),
    ]
    levers = [
        "Add unit test / verifier case with Barrier present and DRMax > Barrier capacity",
        "Instrument runtime path with Frida (A3) on a legal build to observe actual order",
        "Document the order explicitly in evidence limitation until runtime confirmation",
    ]
    strategy = (
        "Keep static diagnosis, mark residual as medium, schedule A3 Frida confirmation "
        "in a later iteration; do not claim high confidence on order until observed."
    )

    best = (
        "effective = Glyph(Barrier.absorb(buffed) - Normal(DRMin,DRMax)); "
        "Barrier is applied before DR subtraction in the static source order."
    )
    inversion = (
        "Barrier.absorb is NOT applied before DR. Either DR is subtracted first, "
        "or a glyph/buff path exists that effectively applies absorption after DR, "
        "making the static source order misleading for real combat outcomes."
    )

    survived = [
        "Raw roll formula (NormalIntRange * aug + Uniform) remains intact",
        "DRMax = tier*(2+lvl) with overflow formula remains intact",
        "Glyph wrapping of the final value remains intact",
    ]
    weakened = [
        "Confidence that Barrier always precedes DR drops from ~0.95 (static) to medium",
    ]
    killed: List[str] = []
    shifted = [
        "Order of Barrier vs DR is now an open residual rather than a closed fact",
        "Need for runtime (Frida) or additional static glyph-path audit increased",
    ]

    changeable = [
        "Verifier can be extended with Barrier+high-DR test vectors",
        "A3 Frida non-root path can observe live order on a legal APK",
    ]
    resistant = [
        "Source-level order in MeleeWeapon is fixed by upstream GPLv3 project",
        "We do not modify SPD source; only observe and document",
    ]
    residual_levers = [
        "Frida gadget hook on Barrier.absorb and DR calculation",
        "Additional static audit of every Glyph that overrides damage processing",
    ]

    stress_diag = (
        "Static source order is Barrier.absorb then DR subtraction, then Glyph. "
        "This order largely survived adversarial inversion, but remains only medium-confidence "
        "until runtime confirmation; no evidence of an inverting glyph path was found in this pass."
    )
    survival = "partially reframed"
    residual = (
        "Barrier vs DR order: static evidence supports Barrier-first; "
        "absence of exhaustive glyph-path audit and missing runtime observation "
        "keep residual at medium. No counter-example found, but not fully closed."
    )
    confidence = 0.72
    boundary = {
        "changeable": changeable,
        "systemically_resistant": resistant,
        "residual_levers": residual_levers,
    }
    method = (
        "AAP v1.2 full loop. Inversion treated as temporarily true. "
        "Survival Assessment: partially reframed. "
        "No strawman; residual explicitly retained."
    )

    result = AAPResult(
        phase0_intent=intent,
        phase0_access_limitations=access,
        phase0_residual_uncertainty=uncertainty,
        phase1_incident=incident,
        phase1_patterns=patterns,
        phase1_architecture=architecture,
        phase1_higher_order_cause=higher_cause,
        phase1_rivals=rivals,
        phase1_levers=levers,
        phase1_strategy=strategy,
        phase2_inversion=inversion,
        phase3_survived=survived,
        phase3_weakened=weakened,
        phase3_killed=killed,
        phase3_shifted=shifted,
        phase4_changeable=changeable,
        phase4_resistant=resistant,
        phase4_residual_levers=residual_levers,
        stress_tested_diagnosis=stress_diag,
        survival_assessment=survival,
        residual=residual,
        overall_confidence=confidence,
        boundary_map=boundary,
        method_note=method,
    )

    check_closure_allowed(result)
    return result


def main() -> None:
    print("=== IrsanAI Torwart (Goalkeeper) AAP v1.2 – SPD Residual: Barrier vs DR ===\n")
    result = run_spd_barrier_dr_residual()
    print(result.to_json())
    print("\n--- Survival Assessment ---")
    print(result.survival_assessment)
    print("--- Residual ---")
    print(result.residual)
    print("--- Confidence ---")
    print(result.overall_confidence)
    print("\n[+] Closure allowed (AAP v1.2 complete)")


if __name__ == "__main__":
    main()
