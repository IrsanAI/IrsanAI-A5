# providers/ – A1 / A3 stubs

These are placeholders for the next iteration.
No live Ghidra / Frida binaries are shipped.

## A1 – MCP Provider stub

`a1_rea_mcp_provider.py` will expose a minimal MCP surface that:

- accepts a target path
- invokes ReaGhidraBridge headless (Ghidra 12.1.x + JDK21)
- returns decompilation artefacts + SHA256
- never performs decompilation itself (orchestration only)

## A3 – Frida Gadget non-root stub

`a3_frida_gadget_stub.sh` will:

- locate a non-root Frida Gadget for Android
- inject into a legal target process
- export basic hooks (open, read, write, SSL)
- feed observations back into the Evidence-Graph

Both stubs remain non-functional until the Maintainer + Reviewer agree on the exact interface.
