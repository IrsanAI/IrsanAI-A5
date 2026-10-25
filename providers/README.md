# providers/ – A1 / A3

No live Ghidra or Frida binaries are shipped.

## A1 – MCP Provider stub
`a1_mcp_provider_stub.py` – orchestration interface only (ReaGhidraBridge protocol).

## A3 – Frida Gadget non-root (Iteration 3)

`a3_frida_gadget_stub.py`:

- `non_root_only=True` enforced (root rejected)
- Optional live path if `frida` Python module + USB device are present
- Always writes evidence JSON under `$HOME/a5_evidence/`
- Claims **observed** only when live attach produced hook data; otherwise **inferred**
- Includes SPD Barrier / DR order probe script template (legal GPLv3 target only)

### Usage

```bash
python3 providers/a3_frida_gadget_stub.py
# → mode=stub without device; evidence JSON still written

python3 torwart/mandatory_inversion.py --i3
# → partially reframed / 0.72

python3 torwart/mandatory_inversion.py --i3 --live 3
# → largely survived / 0.88 – only with real observations EOF
