#!/usr/bin/env python3
"""
A1 – REA MCP Provider Stub (Interface only)

Orchestration only. Does NOT decompile itself.
Delegates to ReaGhidraBridge headless (Ghidra 12.1.x + JDK21).

This file defines the expected interface for Iteration 2+.
No live Ghidra / REA execution is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol


@dataclass
class DecompileRequest:
    target_path: str
    architecture: Optional[str] = None
    language: Optional[str] = None
    timeout_sec: int = 300


@dataclass
class DecompileArtifact:
    target_path: str
    sha256: str
    decompiled_path: Optional[str] = None
    functions: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ReaGhidraBridge(Protocol):
    def headless_decompile(self, req: DecompileRequest) -> DecompileArtifact:
        ...


class A1McpProvider:
    def __init__(self, bridge: Optional[ReaGhidraBridge] = None):
        self._bridge = bridge

    def decompile(self, req: DecompileRequest) -> DecompileArtifact:
        if self._bridge is None:
            return DecompileArtifact(
                target_path=req.target_path,
                sha256="",
                error="stub only – no ReaGhidraBridge bound; orchestration interface ready",
            )
        return self._bridge.headless_decompile(req)

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "a1_rea_mcp",
            "status": "stub",
            "bridge_bound": self._bridge is not None,
            "note": "Interface only. No decompilation performed.",
        }


if __name__ == "__main__":
    p = A1McpProvider()
    print(p.health())
    art = p.decompile(DecompileRequest(target_path="${HOME}/example.so"))
    print(art)
