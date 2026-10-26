#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import json, argparse, pathlib, time
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
    """STRICT v2.1: 0.88 nur wenn echte korrelierte Barrier Evidence mit realer SHA + device_id + frischer ts"""
    if finding_id != "spd_barrier_dr_order":
        return 0
    ev_dir = pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists():
        return 0
    cnt=0
    now=time.time()
    for f in ev_dir.glob("*.json"):
        try:
            j=json.loads(f.read_text(encoding="utf-8")[:8000])
            if j.get("finding_id")!=finding_id: continue
            if j.get("provider")!="a3_frida": continue
            if j.get("target")!="spd": continue
            if j.get("confidence")!="observed": continue
            if not j.get("correlated"): continue
            obs=j.get("observed",{})
            # muss Barrier betreffen, nicht irgendein ShieldBuff
            bclass=obs.get("barrier_class") or obs.get("buffType") or ""
            if "Barrier" not in bclass: continue
            if obs.get("barrier_absorb_value") is None: continue
            if obs.get("dr_roll") is None and obs.get("dr_min") is None: continue
            if obs.get("damage_roll") is None: continue
            if obs.get("order")!="dr_before_barrier": continue
            # muss attack_id haben (per-attack binding)
            if obs.get("attack_id") is None: continue
            # SHA + device_id dürfen nicht Placeholder sein
            sha=j.get("binary_sha256") or ""
            if not sha or "unknown" in sha or "needs-real" in sha or len(sha)<16: continue
            dev=j.get("device_id") or ""
            if not dev or "fallback" in dev or "needs-real" in dev: continue
            frida_v=j.get("frida_version") or ""
            if not frida_v: continue
            # frisch <24h
            ts=j.get("ts") or j.get("timestamp") or 0
            # timestamp kann ms sein
            if ts>1e12: ts=ts/1000
            if now - float(ts) > 86400: continue
            cnt+=1
        except: pass
    return cnt

def check_closure_allowed(r: AAPResult):
    # 0.88 darf nur wenn real>0 und SPD live implementiert
    if r.overall_confidence > 0.8:
        if "not implemented" in r.phase0_access_limitations.lower():
            # wenn noch als not implemented markiert, darf nicht 0.88
            raise Exception("Closure blocked: still marked not implemented")
        # ansonsten braucht es real>0
        if count_real_observed("spd_barrier_dr_order")==0:
            raise Exception("Closure blocked: 0.88 requires real correlated Barrier evidence")
    if r.phase0_residual_uncertainty=="high" and r.overall_confidence>0.7:
        raise Exception("Closure blocked: high residual must be <=0.7")
    return True

def run_spd_barrier_dr_residual():
    return AAPResult(
        "SPD Barrier vs DR – static DR before Barrier, live not yet verified",
        "Static analysis: Char.attack() dr = drRoll() -> max(eff-dr,0) -> damage() -> ShieldBuff.processDamage -> Barrier.absorbDamage. Live verification pending – need real APK SHA + device_id + correlated Barrier absorb in same attack. Fail-closed 0.72 until then.",
        "medium",
        "Static: DR before Barrier – needs live correlated verification",
        ["Barrier Buff absorb","DR Normal roll","ShieldBuff.processDamage"],
        "Char.attack: damageRoll -> defenseProc -> drRoll -> effective-dr -> damage -> processDamage -> absorbDamage",
        "DR before Barrier (static hypothesis, plausible)",
        [RivalExplanation("order irrelevant",True), RivalExplanation("glyph re-introduces",True)],
        ["Build real APK with Gadget","Implement per-attack correlated hook (Barrier-only, reset after absorb)","Verifier with attack_id + SHA + device_id + freshness"],
        "Keep 0.72 until real SPD Frida run with correlated Barrier absorb in same attack",
        "Barrier NOT before DR – DR first",
        ["Raw roll formula intact","DR before Barrier static"],["Confidence medium – needs live"],[],["Need SPD runtime with Frida correlated"],
        ["Build SPD APK","Real Frida hook per-attack"],["Source fixed upstream"],
        ["Frida SPD hook – must capture Barrier.absorb value AND DR in SAME attack_id, reset after"],
        "Static DR before Barrier plausible, supported by Char.java:390 drRoll -> 483 defenseProc -> max(eff-dr) -> 987 processDamage -> absorbDamage. Live needs per-attack correlated Barrier observation.",
        "partially reframed",
        "Static DR before Barrier plausible – 0.72 fail-closed – 0.88 requires real APK SHA + device_id + correlated Barrier absorb in same attack_id, fresh <24h",
        0.72,
        {"changeable":["Real APK + per-attack hook"]},
        "AAP v1.2 FINAL HONEST – SPD static DR before Barrier, live pending, fail-closed 0.72"
    )

def run_spd_barrier_dr_residual_i3(live_observations: int = 0):
    FINDING="spd_barrier_dr_order"
    real = count_real_observed(FINDING)
    base = run_spd_barrier_dr_residual()
    if live_observations>0:
        if real>0:
            print(f"[+] Torwart v2.1: --live {live_observations} real_correlated_Barrier={real} -> 0.88 LARGELY SURVIVED (DR before Barrier verified live)")
            base.phase0_intent=f"i3 v2.1 – {FINDING} – live verified – real={real} correlated Barrier"
            base.phase0_access_limitations=f"Real APK SHA + device_id + correlated Barrier absorb in same attack_id present – real={real} – 0.88 allowed"
            base.overall_confidence=0.88
            base.survival_assessment="largely survived"
            base.residual=f"Live verified: DR before Barrier, {real} correlated Barrier absorb(s) in same attack_id, fresh <24h"
            base.method_note=f"AAP v2.1 live verified – DR before Barrier – {real} correlated"
        else:
            print(f"[!] Torwart v2.1: --live {live_observations} für {FINDING} – no real correlated Barrier evidence (SHA/device_id/freshness/Barrier check) – real={real} – bleibe bei 0.72")
            base.phase0_intent=f"i3 v2.1 – {FINDING} – no real correlated Barrier evidence – live requested {live_observations} real={real}"
            base.overall_confidence=0.72
            base.survival_assessment="partially reframed"
    check_closure_allowed(base)
    return base

def main():
    p=argparse.ArgumentParser(); p.add_argument("--i3",action="store_true"); p.add_argument("--live",type=int,default=0); a=p.parse_args()
    if a.i3:
        r=run_spd_barrier_dr_residual_i3(a.live)
        print(f"=== Torwart v2.1 – i3 live={a.live} real_correlated={count_real_observed()} ===\n")
    else:
        r=run_spd_barrier_dr_residual()
    print(r.to_json()); print(f"\n--- {r.survival_assessment} {r.overall_confidence} ---\n{r.residual}")

if __name__=="__main__": main()
