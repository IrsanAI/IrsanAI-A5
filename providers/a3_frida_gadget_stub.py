#!/usr/bin/env python3
"""
A3 – Frida Gadget non-root Provider (Iteration 3) – fixed API compat
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import json, os, hashlib

class HookTarget(str, Enum):
    OPEN="open"; READ="read"; WRITE="write"; SSL="ssl"; CUSTOM="custom"
    BARRIER_ABSORB="barrier_absorb"; DR_ROLL="dr_roll"; DAMAGE_ROLL="damage_roll"

@dataclass
class FridaAttachRequest:
    package_or_pid: str
    gadget_path: Optional[str]=None
    hooks: List[HookTarget]=field(default_factory=lambda:[HookTarget.BARRIER_ABSORB, HookTarget.DR_ROLL, HookTarget.DAMAGE_ROLL])
    script_source: Optional[str]=None
    timeout_sec: int=60
    non_root_only: bool=True
    evidence_dir: Optional[str]=None

@dataclass
class FridaObservation:
    hook: str; timestamp: str; data: Dict[str, Any]; sha256_context: Optional[str]=None

@dataclass
class FridaSessionResult:
    package_or_pid: str; attached: bool; mode: str
    observations: List[FridaObservation]=field(default_factory=list)
    error: Optional[str]=None; note: str=""; evidence_id: Optional[str]=None; evidence_path: Optional[str]=None
    def to_dict(self): return asdict(self)

def _default_evidence_dir(): return os.path.join(os.environ.get("HOME") or os.path.expanduser("~"), "a5_evidence")
def _frida_available():
    try: import frida; return True
    except ImportError: return False

SPD_BARRIER_DR_SCRIPT = r"""
Java.perform(function(){var log=function(t,o){send({hook:t,ts:Date.now(),data:[STRIPPED]
try{var B=Java.use("com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Barrier");if(B.absorb){B.absorb.implementation=function(d){var b=d;var a=this.absorb(d);log("barrier_absorb",{before:b,after:a});return a;}}}catch(e){log("barrier_absorb_error",{message:String(e)})}
try{var M=Java.use("com.shatteredpixel.shatteredpixeldungeon.items.weapon.melee.MeleeWeapon");if(M.damageRoll){M.damageRoll.overload().implementation=function(){var v=this.damageRoll();log("damage_roll",{value:v});return v;}}}catch(e){log("damage_roll_error",{message:String(e)})}
send({hook:"script_loaded",ts:Date.now(),data:[STRIPPED]
"""

class A3FridaGadgetProvider:
    def health(self):
        return {"provider":"a3_frida_gadget","status":"ready" if _frida_available() else "stub","frida_module":_frida_available(),"non_root_only":True,"note":"No Frida binary redistributed."}
    def attach(self, req: FridaAttachRequest):
        if not req.non_root_only:
            return FridaSessionResult(req.package_or_pid, False, "rejected", error="root paths are out of scope; non_root_only is mandatory", note="rejected")
        script=req.script_source or SPD_BARRIER_DR_SCRIPT
        observations=[]; attached=False; mode="stub"; error=None; note="stub – no device"
        if _frida_available():
            try:
                import frida, time
                device=None
                # try old API
                try:
                    device=frida.get_usb_device(timeout=min(5, req.timeout_sec))
                except AttributeError:
                    device=None
                # new API fallback
                if device is None:
                    try:
                        for d in frida.enumerate_devices():
                            dtype=getattr(d,'type',''); did=getattr(d,'id','')
                            if dtype=='usb' or 'usb' in did.lower() or dtype=='local':
                                device=d; break
                    except Exception:
                        device=None
                if device is None:
                    raise Exception("no usb/local device found (emulator/device not attached)")
                session=device.attach(req.package_or_pid)
                sc=session.create_script(script)
                def on_message(m,d):
                    if m.get("type")=="send":
                        p=m.get("payload") or {}
                        observations.append(FridaObservation(str(p.get("hook","unknown")), datetime.now(timezone.utc).isoformat(), p.get("data") or p))
                sc.on("message", on_message); sc.load(); attached=True; mode="live"; note="live non-root attach; observations collected"
                time.sleep(min(2, req.timeout_sec)); session.detach()
            except Exception as exc:
                error=f"live attach failed: {exc}"; mode="stub"; note="frida present but attach failed – see error"; attached=False
        result=FridaSessionResult(req.package_or_pid, attached, mode, observations, error, note)
        evidence_dir=req.evidence_dir or _default_evidence_dir(); os.makedirs(evidence_dir, exist_ok=True)
        eid=f"a3-frida-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"; epath=os.path.join(evidence_dir, f"{eid}.json")
        confidence="observed" if (mode=="live" and observations) else "inferred"; score=0.9 if confidence=="observed" else 0.55
        payload={"evidence_id":eid,"target":req.package_or_pid,"provider":"a3_frida_gadget","offset":"barrier_absorb|dr_roll|damage_roll","sha256":hashlib.sha256(json.dumps(result.to_dict(), sort_keys=True, default=str).encode()).hexdigest(),"confidence":confidence,"confidence_score":score,"limitation":"live Frida observations" if confidence=="observed" else "no live device/frida – attempt logged as inferred only","mode":mode,"attached":attached,"observation_count":len(observations),"created_at":datetime.now(timezone.utc).isoformat()}
        with open(epath,"w",encoding="utf-8") as f: json.dump(payload,f,indent=2,ensure_ascii=False)
        result.evidence_id=eid; result.evidence_path=epath; return result

if __name__=="__main__":
    p=A3FridaGadgetProvider(); print("health:", p.health())
    res=p.attach(FridaAttachRequest(package_or_pid="com.shatteredpixel.shatteredpixeldungeon", non_root_only=True))
    print("mode:", res.mode, "attached:", res.attached); print("evidence:", res.evidence_id, res.evidence_path)
    if res.error: print("error:", res.error)
