#!/usr/bin/env python3
"""
A3 – Frida Gadget non-root Stub (Interface only)

Dynamic truth layer for Android targets.
Gadget is intended for non-root use only.
No Frida binaries or gadget payloads are shipped or executed by this stub.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class HookTarget(str, Enum):
    OPEN = "open"
    READ = "read"
    WRITE = "write"
    SSL = "ssl"
    CUSTOM = "custom"


@dataclass
class FridaAttachRequest:
    package_or_pid: str
    gadget_path: Optional[str] = None
    hooks: List[HookTarget] = field(default_factory=lambda: [HookTarget.OPEN, HookTarget.READ])
    script_source: Optional[str] = None
    timeout_sec: int = 60
    non_root_only: bool = True


@dataclass
class FridaObservation:
    hook: str
    timestamp: str
    data: Dict[str, Any]
    sha256_context: Optional[str] = None


@dataclass
class FridaSessionResult:
    package_or_pid: str
    attached: bool
    observations: List[FridaObservation] = field(default_factory=list)
    error: Optional[str] = None
    note: str = "stub only – no live Frida gadget executed"


class A3FridaGadgetProvider:
    def __init__(self):
        self._sessions: Dict[str, Any] = {}

    def attach(self, req: FridaAttachRequest) -> FridaSessionResult:
        if not req.non_root_only:
            return FridaSessionResult(
                package_or_pid=req.package_or_pid,
                attached=False,
                error="root paths are out of scope; non_root_only is mandatory",
            )
        return FridaSessionResult(
            package_or_pid=req.package_or_pid,
            attached=False,
            error="stub only – interface ready, no Frida binary present",
            note="Gadget non-root path; no execution in this iteration",
        )

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "a3_frida_gadget",
            "status": "stub",
            "non_root_only": True,
            "note": "Interface only. No Frida Gadget binary is redistributed or executed.",
        }


if __name__ == "__main__":
    p = A3FridaGadgetProvider()
    print(p.health())
    res = p.attach(FridaAttachRequest(package_or_pid="com.example.legal.target"))
    print(res)
