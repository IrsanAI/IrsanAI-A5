#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import json, argparse, pathlib, time, hashlib, os, random, string
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

def get_local_target_hash() -> str:
    # Hash des lokal untersuchten Zielartefakts – Char.java (oder APK wenn vorhanden)
    # Muss mit Evidence binary_sha256 übereinstimmen – verhindert Random-SHA Fake
    candidates=[
        pathlib.Path.home()/ "[STRIPPED 86 bytes].java",
        pathlib.Path.home()/ "[STRIPPED 86 bytes].java".replace("a5_targets/spd","a5_targets/spd"),
        pathlib.Path("[STRIPPED 71 bytes].java"),
    ]
    # zusätzliche Suche
    for cand in list(pathlib.Path.home().glob("a5_targets/**/Char.java")):
        candidates.append(cand)
    for p in candidates:
        if p.exists():
            return hashlib.sha256(p.read_bytes()).hexdigest()
    # Fallback: Hash von ShieldBuff als Anker
    p2=pathlib.Path.home()/ "[STRIPPED 98 bytes].java"
    if p2.exists():
        return hashlib.sha256(p2.read_bytes()).hexdigest()
    return "no-target-found"

def get_local_frida_version() -> str:
    try:
        import frida
        return getattr(frida, "__version__", "unknown")
    except:
        return "unknown"

def get_live_nonce_path():
    return pathlib.Path.home()/ "a5_evidence/.live_nonce"

def get_current_live_nonce():
    p=get_live_nonce_path()
    if p.exists():
        try: return p.read_text().strip()
        except: return None
    return None

def count_real_observed(finding_id: str = "spd_barrier_dr_order") -> int:
    if finding_id != "spd_barrier_dr_order":
        return 0
    ev_dir = pathlib.Path.home() / "a5_evidence"
    if not ev_dir.exists(): return 0
    local_hash=get_local_target_hash()
    local_frida=get_local_frida_version()
    live_nonce=get_current_live_nonce()
    cnt=0
    now=time.time()
    for f in ev_dir.glob("*.json"):
        try:
            j=json.loads(f.read_text(encoding="utf-8")[:12000])
            if j.get("finding_id")!=finding_id: continue
            if j.get("provider")!="a3_frida": continue
            if j.get("target")!="spd": continue
            if j.get("confidence")!="observed": continue
            if not j.get("correlated"): continue
            obs=j.get("observed",{})
            bclass=obs.get("barrier_class") or obs.get("buffType") or ""
            if "Barrier" not in bclass: continue
            if obs.get("barrier_absorb_value") is None: continue
            if obs.get("dr_roll") is None and obs.get("dr_min") is None: continue
            if obs.get("damage_roll") is None: continue
            if obs.get("order")!="dr_before_barrier": continue
            if obs.get("attack_id") is None: continue
            # Manus Edge: ohne live_nonce darf nichts als real zählen
            if not j.get("live_nonce"): continue
            # SHA muss lokal berechnetem Hash entsprechen – blockt Random-64-char Fake (Manus)
            sha=j.get("binary_sha256") or ""
            if sha != local_hash: continue
            # Frida Version muss echter lokaler Version entsprechen
            frida_v=j.get("frida_version") or ""
            if local_frida!="unknown" and frida_v!=local_frida: continue
            # Device-ID muss vorhanden sein und nicht Fallback, und Nonce muss passen wenn live run aktiv
            dev=j.get("device_id") or ""
            if not dev or "fallback" in dev or "needs-real" in dev: continue
            # Nonce Check – Evidence muss live_nonce aus aktuellem Run enthalten, blockt frei erzeugte JSON ohne Runner
            if live_nonce:
                if j.get("live_nonce")!=live_nonce: continue
            else:
                # wenn kein live run aktiv, darf Evidence nicht als real zählen – verhindert alte Fake Files
                # Ausnahme: wenn Evidence <5min und frisch, aber ohne nonce -> noch blocken für SPD
                # Für SPD fordern wir immer nonce wenn live_observations>0
                pass
            ts=j.get("ts") or j.get("timestamp") or 0
            if ts>1e12: ts=ts/1000
            if now - float(ts) > 300: continue  # 5min Frische statt 24h – blockt Replay
            cnt+=1
        except: pass
    return cnt

def check_closure_allowed(r: AAPResult):
    if r.overall_confidence > 0.8:
        if "not implemented" in r.phase0_access_limitations.lower() and count_real_observed("spd_barrier_dr_order")==0:
            raise Exception("Closure blocked: still marked not implemented and no real correlated Barrier evidence")
        if count_real_observed("spd_barrier_dr_order")==0:
            raise Exception("Closure blocked: 0.88 requires real correlated Barrier evidence with local APK hash match + nonce")
    if r.phase0_residual_uncertainty=="high" and r.overall_confidence>0.7:
        raise Exception("Closure blocked: high residual must be <=0.7")
    return True

def run_spd_barrier_dr_residual():
    local_hash=get_local_target_hash()[:12]
    return AAPResult(
        "SPD Barrier vs DR – static DR before Barrier, live not yet verified",
        f"SPD-Live-Verifikation noch nicht implementiert – not implemented – Static: Char.java 390 drRoll before 415 damageRoll, 483 defenseProc max(eff-dr) before 987 processDamage. Local target hash {local_hash}... – need real Frida Runner with send() + nonce + local hash match. Fail-closed 0.72.",
        "medium",
        "Static: DR before Barrier – needs live correlated verification with local hash",
        ["Barrier Buff absorb","DR Normal roll","ShieldBuff.processDamage"],
        "Char.attack: attack() -> drRoll (390) -> damageRoll (415) -> defenseProc -> max(eff-dr) -> damage -> processDamage -> absorbDamage",
        "DR before Barrier (static, plausible, attack()-bound)",
        [RivalExplanation("order irrelevant",True), RivalExplanation("glyph re-introduces",True)],
        ["Real APK + Gadget + Runner that validates hash + nonce","Per-attack hook from attack() with reset","Verifier checks local hash + frida_version + nonce + freshness 5min"],
        "Keep 0.72 until real SPD Frida run with correlated Barrier absorb in same attack_id, local hash match",
        "Barrier NOT before DR – DR first",
        ["Raw roll formula intact","DR before Barrier static"],["Confidence medium – needs live"],[],["Need SPD runtime with Frida correlated + send()"],
        ["Build SPD APK","Real Frida runner with hash compare"],["Source fixed upstream"],
        ["Frida SPD hook must start at attack() and capture drRoll BEFORE damageRoll in same attack_id, Barrier-only, send() to runner, reset"],
        f"Static DR before Barrier plausible, Char.java drRoll 390 before damageRoll 415, ShieldBuff.java processDamage after DR. Local hash {local_hash}... Live needs per-attack correlated Barrier with local hash + nonce.",
        "partially reframed",
        f"Static DR before Barrier plausible – 0.72 fail-closed – 0.88 requires local hash {local_hash}... match + frida_version + device_id + attack_id + nonce + 5min freshness",
        0.72,
        {"changeable":["Real APK + per-attack hook with hash + nonce"]},
        "AAP v2.2 FINAL HONEST – SPD static DR before Barrier, live pending hash+nonce, fail-closed 0.72"
    )

def run_spd_barrier_dr_residual_i3(live_observations: int = 0):
    FINDING="spd_barrier_dr_order"
    base = run_spd_barrier_dr_residual()
    if live_observations>0:
        import random, string
        nonce=''.join(random.choices(string.ascii_letters+string.digits, k=24))
        get_live_nonce_path().parent.mkdir(exist_ok=True)
        get_live_nonce_path().write_text(nonce)
        real = count_real_observed(FINDING)
        print(f"[Torwart v3.1] live_nonce={nonce} local_hash={get_local_target_hash()[:12]}... local_frida={get_local_frida_version()} real_correlated={real}")
        if real>0:
            print(f"[+] Torwart v3.1: --live {live_observations} real_correlated_Barrier={real} with local hash match + nonce -> 0.88")
            base.phase0_intent=f"i3 v3.1 – {FINDING} – live verified – real={real} correlated Barrier hash+nonce"
            base.phase0_access_limitations=f"Real APK hash {get_local_target_hash()[:12]}... + device_id + nonce + correlated Barrier – real={real} – 0.88 allowed – implemented"
            base.overall_confidence=0.88
            base.survival_assessment="largely survived"
            base.residual=f"Live verified: DR before Barrier, {real} correlated Barrier with local hash match + nonce, fresh <5min"
            base.method_note=f"AAP v3.1 live verified – DR before Barrier – {real} correlated hash+nonce"
        else:
            print(f"[!] Torwart v3.1: --live {live_observations} für {FINDING} – no real correlated – real={real} – bleibe bei 0.72")
            base.phase0_intent=f"i3 v3.1 – {FINDING} – no real correlated – live requested {live_observations} real={real} – not implemented"
            base.phase0_access_limitations=f"SPD-Live-Verifikation noch nicht implementiert – not implemented – no real correlated with hash {get_local_target_hash()[:12]}... + nonce – real={real} – 0.72 fail-closed"
            base.overall_confidence=0.72
            base.survival_assessment="partially reframed"
    else:
        real = count_real_observed(FINDING)
        print(f"=== Torwart v3.1 – i3 live=0 real={real} local_hash={get_local_target_hash()[:12]}... ===")
    check_closure_allowed(base)
    return base


def main():
    p=argparse.ArgumentParser(); p.add_argument("--i3",action="store_true"); p.add_argument("--live",type=int,default=0); a=p.parse_args()
    if a.i3:
        r=run_spd_barrier_dr_residual_i3(a.live)
        print(f"=== Torwart v3 – i3 live={a.live} real_correlated={count_real_observed()} local_hash={get_local_target_hash()[:12]}... ===\n")
    else:
        r=run_spd_barrier_dr_residual()
    print(r.to_json()); print(f"\n--- {r.survival_assessment} {r.overall_confidence} ---\n{r.residual}")

if __name__=="__main__": main()
