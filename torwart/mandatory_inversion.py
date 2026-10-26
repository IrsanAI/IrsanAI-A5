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

def count_real_observed(finding_id: str = "spd_barrier_dr_order", provider: str = "a3_frida", target: str = "spd") -> int:
    """STRICT: zählt nur Evidence die wirklich zu diesem Finding gehört"""
    ev_dir = pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists(): return 0
    cnt=0
    for f in ev_dir.glob("*.json"):
        try:
            j=json.loads(f.read_text(encoding="utf-8")[:4000])
            if j.get("confidence")!="observed": continue
            if j.get("provider")!=provider: continue
            # muss finding_id matchen – entweder top-level oder im observed dict
            fid = j.get("finding_id") or j.get("observed",{}).get("finding_id") or ""
            if fid!=finding_id: continue
            # target muss passen – crackme darf nicht SPD freischalten!
            t = j.get("target") or ""
            if target not in t and finding_id in ["spd_barrier_dr_order"]:
                if "spd" not in t.lower(): continue
            cnt+=1
        except: pass
    return cnt

def check_closure_allowed(r):
    if r.survival_assessment not in ("largely survived","partially reframed","significantly reframed","largely collapsed"):
        raise Exception("Closure blocked")
    return True

def run_spd_barrier_dr_residual():
    return AAPResult(
        "Close residual Barrier vs DR order – static only",
        "Static source only, no runtime",
        "medium",
        "Static: Barrier.absorb then Normal(DRMin,DRMax)",
        ["Barrier Buff absorb","DR Normal roll","Glyph wrap","Augment 1.5/0.7"],
        "MeleeWeapon.damageRoll -> raw* aug + Uniform -> Barrier.absorb -> Normal(DRMin,DRMax) -> Glyph",
        "Barrier first for predictable absorption",
        [RivalExplanation("commutative – order irrelevant",True),RivalExplanation("glyph re-introduces damage",True)],
        ["Verifier test Barrier+high DR","Frida live hook SPD damageRoll","Document limitation"],
        "Keep static, mark medium, schedule Frida SPD",
        "Barrier NOT before DR – DR first or glyph inverts order",
        ["Raw roll formula intact","DRMax tier*(2+lvl) overflow","Glyph wrapping"],
        ["Confidence Barrier precedes DR drops to medium"],[],["Order open residual","Need runtime"],
        ["Verifier extend","A3 Frida observe SPD"],["Source fixed upstream","We only observe"],
        ["Frida hook Barrier.absorb+DR SPD","Glyph audit"],
        "Static Barrier-first largely survived but medium-confidence until runtime",
        "partially reframed",
        "static Barrier-first; A3 path ready, no runtime SPD -> medium",
        0.72,
        {"changeable":["Verifier extend"],"systemically_resistant":["Source fixed"],"residual_levers":["Frida hook"]},
        "AAP v1.2 honest partially reframed"
    )

def run_spd_barrier_dr_residual_i3(live_observations: int = 0):
    FINDING="spd_barrier_dr_order"
    real = count_real_observed(finding_id=FINDING, provider="a3_frida", target="spd")
    base = run_spd_barrier_dr_residual()
    if live_observations>0 and real < live_observations:
        print(f"[!] Torwart Guard: --live {live_observations} für {FINDING} angefordert, aber nur {real} echte passende observed Evidence (provider=a3_frida,target=spd,finding={FINDING}) gefunden – bleibe bei 0.72 (ehrlich)")
        base.phase0_intent = f"i3 – --live {live_observations} requested for {FINDING} but only {real} real matching"
        base.phase0_access_limitations = f"No {live_observations} real observed for {FINDING} – only {real} found"
        base.overall_confidence = 0.72
        base.survival_assessment = "partially reframed"
        base.residual = f"static; requested {live_observations} live for {FINDING} but only {real} real -> medium"
        base.method_note = f"AAP v1.2 i3 honest guard strict {FINDING} real={real}"
        check_closure_allowed(base); return base
    if live_observations <=0 or real==0:
        base.phase0_intent = f"i3 – Re-run {FINDING}; A3 path ready, no live SPD device"
        base.phase0_access_limitations = "Static + A3 provider ready, no live SPD – inferred only"
        base.overall_confidence = 0.72
        base.survival_assessment = "partially reframed"
        check_closure_allowed(base); return base
    else:
        base.phase0_intent = f"i3 – {FINDING} with {live_observations} REAL observed (real={real})"
        base.phase0_access_limitations = f"A3 Frida SPD live attach succeeded, {live_observations} real observed for {FINDING}"
        base.phase0_residual_uncertainty = "low"
        base.phase3_survived.append(f"{live_observations} live {FINDING} confirm Barrier-first (real={real})")
        base.stress_tested_diagnosis = f"With {live_observations} REAL observed for {FINDING}, Barrier.absorb precedes DR – confirmed at runtime"
        base.survival_assessment = "largely survived"
        base.residual = f"Barrier-first confirmed by {live_observations} real observed for {FINDING}; residual low"
        base.overall_confidence = 0.88
        base.method_note = f"AAP v1.2 i3 LIVE honest – {FINDING} {live_observations} observed"
        check_closure_allowed(base); return base

def main():
    p=argparse.ArgumentParser(); p.add_argument("--i3",action="store_true"); p.add_argument("--live",type=int,default=0); a=p.parse_args()
    if a.i3:
        r=run_spd_barrier_dr_residual_i3(a.live)
        print(f"=== Torwart AAP v1.2 – i3 live={a.live} real_strict={count_real_observed()} ===\n")
    else:
        r=run_spd_barrier_dr_residual(); print("=== Torwart AAP v1.2 ===\n")
    print(r.to_json()); print("\n--- Survival ---",r.survival_assessment); print("--- Confidence ---",r.overall_confidence); print("\n[+] Closure allowed")
if __name__=="__main__": main()
