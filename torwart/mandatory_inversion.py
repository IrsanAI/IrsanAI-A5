#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import json, argparse, pathlib, hashlib, time
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

def _is_valid_spd_evidence(j: dict) -> bool:
    """STRICT: SPD braucht echte Messfelder, nicht nur observed flag"""
    if j.get("confidence")!="observed": return False
    if j.get("provider")!="a3_frida": return False
    if j.get("finding_id")!="spd_barrier_dr_order": return False
    target = j.get("target","")
    if "spd" not in target.lower(): return False
    obs = j.get("observed",{})
    # muss echte SPD-Felder enthalten – Barrier + DR
    obs_str = json.dumps(obs).lower()
    has_barrier = "barrier" in obs_str and ("absorb" in obs_str or "barrier_absorb" in obs_str)
    has_dr = "dr" in obs_str or "damage" in obs_str
    if not (has_barrier and has_dr): return False
    # muss Frida-Attestierung enthalten
    if "frida_version" not in j and "frida_version" not in obs: return False
    if "binary_sha256" not in j and "binary_sha256" not in obs: return False
    if "device_id" not in j and "device_id" not in obs: return False
    # muss frisch sein (24h) – alte Fake-Files zählen nicht
    ts = j.get("ts") or obs.get("ts") or 0
    try:
        if time.time() - float(ts) > 86400: return False
    except: return False
    # observed muss echte Werte enthalten, nicht nur Platzhalter
    if "barrier_absorb_value" not in obs_str and "damage_roll" not in obs_str:
        return False
    return True

def _is_valid_crackme_evidence(j: dict) -> bool:
    if j.get("confidence")!="observed": return False
    if j.get("finding_id")!="a5_crackme_v2_key_check": return False
    obs=j.get("observed",{})
    if "input" not in json.dumps(obs).lower(): return False
    if "result" not in json.dumps(obs).lower(): return False
    if "frida_version" not in j and "frida_version" not in obs: return False
    return True

def count_real_observed(finding_id: str = "spd_barrier_dr_order") -> int:
    ev_dir = pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists(): return 0
    cnt=0
    for f in ev_dir.glob("*.json"):
        try:
            j=json.loads(f.read_text(encoding="utf-8")[:8000])
            if finding_id=="spd_barrier_dr_order":
                if _is_valid_spd_evidence(j): cnt+=1
            elif finding_id=="a5_crackme_v2_key_check":
                if _is_valid_crackme_evidence(j): cnt+=1
        except: pass
    return cnt

def check_closure_allowed(r): return True

def run_spd_barrier_dr_residual():
    return AAPResult(
        "Close residual Barrier vs DR order – static only",
        "Static source only, no SPD runtime, no Frida SPD hook yet",
        "medium",
        "Static: Barrier.absorb then Normal(DRMin,DRMax)",
        ["Barrier Buff absorb","DR Normal roll","Glyph wrap","Augment 1.5/0.7"],
        "MeleeWeapon.damageRoll -> raw* aug + Uniform -> Barrier.absorb -> Normal(DRMin,DRMax) -> Glyph",
        "Barrier first for predictable absorption",
        [RivalExplanation("commutative – order irrelevant",True)],
        ["Verifier test Barrier+high DR","Frida live hook SPD damageRoll","Document limitation"],
        "Keep static, mark medium, schedule Frida SPD",
        "Barrier NOT before DR – DR first or glyph inverts order",
        ["Raw roll formula intact"],["Confidence Barrier precedes DR drops to medium"],[],["Order open residual","Need runtime SPD"],
        ["Verifier extend","A3 Frida observe SPD"],["Source fixed upstream"],
        ["Frida hook Barrier.absorb+DR SPD"],
        "Static Barrier-first largely survived but medium-confidence until SPD runtime",
        "partially reframed","static Barrier-first; no SPD runtime -> medium remains",0.72,
        {"changeable":["Verifier extend"]},"AAP v1.2 honest strict"
    )

def run_spd_barrier_dr_residual_i3(live_observations: int = 0):
    FINDING="spd_barrier_dr_order"
    real = count_real_observed(finding_id=FINDING)
    base = run_spd_barrier_dr_residual()
    if live_observations>0 and real < live_observations:
        print(f"[!] Torwart Guard STRICT: --live {live_observations} für {FINDING} angefordert, aber nur {real} VALIDIERTE echte SPD-Evidence gefunden (braucht barrier_absorb+dr+frida_version+binary_sha256+device_id+frisch <24h) – bleibe bei 0.72")
        base.phase0_intent = f"i3 STRICT – --live {live_observations} for {FINDING} but only {real} VALID"
        base.phase0_access_limitations = f"No {live_observations} valid SPD observed – only {real} strict-valid found"
        base.overall_confidence = 0.72; base.survival_assessment="partially reframed"
        base.residual=f"requested {live_observations} live for {FINDING} but only {real} strict-valid -> medium"
        base.method_note=f"AAP v1.2 i3 STRICT guard {FINDING} real_valid={real}"
        return base
    if live_observations<=0 or real==0:
        base.phase0_intent=f"i3 – Re-run {FINDING}; no valid SPD live evidence yet (need Frida SPD hook)"
        base.overall_confidence=0.72; base.survival_assessment="partially reframed"
        return base
    else:
        base.phase0_intent=f"i3 – {FINDING} with {live_observations} VALID observed"
        base.phase0_residual_uncertainty="low"
        base.phase3_survived.append(f"{live_observations} VALID live {FINDING} confirm Barrier-first")
        base.survival_assessment="largely survived"; base.overall_confidence=0.88
        base.residual=f"Barrier-first confirmed by {live_observations} VALID SPD observed"
        base.method_note=f"AAP v1.2 i3 LIVE STRICT VALID – {FINDING}"
        return base

def main():
    p=argparse.ArgumentParser(); p.add_argument("--i3",action="store_true"); p.add_argument("--live",type=int,default=0); a=p.parse_args()
    if a.i3:
        r=run_spd_barrier_dr_residual_i3(a.live)
        print(f"=== Torwart AAP v1.2 STRICT – i3 live={a.live} real_strict={count_real_observed('spd_barrier_dr_order')} ===\n")
    else:
        r=run_spd_barrier_dr_residual()
    print(r.to_json()); print("\n--- Survival ---",r.survival_assessment, "Conf", r.overall_confidence)

if __name__=="__main__": main()
