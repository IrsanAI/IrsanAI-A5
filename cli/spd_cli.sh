#!/data/data/com.termux/files/usr/bin/bash
# IrsanAI-A5 – SPD CLI (Termux-First, hardened)
# Never embed long absolute paths as literals (Termux filter strips \~76 bytes).

set -euo pipefail

BASE="${HOME}/shattered-pixel-dungeon"
LOGDIR="${HOME}/spd_logs"
EVIDENCE_DIR="${HOME}/a5_evidence"

[ -d "$LOGDIR" ] || mkdir -p "$LOGDIR"
[ -d "$EVIDENCE_DIR" ] || mkdir -p "$EVIDENCE_DIR"

die() { echo "ERROR: $*" >&2; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

require_cmd find
require_cmd grep
require_cmd sha256sum
require_cmd python3

if [ ! -d "$BASE" ]; then
  die "SPD source tree not found at \$HOME/shattered-pixel-dungeon
Clone it first:
  git clone --depth 1 https://github.com/00-Evan/shattered-pixel-dungeon.git \"\$HOME/shattered-pixel-dungeon\""
fi

MELEE_FILE=$(find "$BASE" -type f -name "MeleeWeapon.java" 2>/dev/null | head -n 1)

if [ -z "$MELEE_FILE" ]; then
  die "MeleeWeapon.java not found under $BASE"
fi

echo "[*] Found: $MELEE_FILE"

OUT_MELEE="${LOGDIR}/melee_damageRoll.txt"
grep -n -A 12 -E "damageRoll|DRMax|Barrier" "$MELEE_FILE" > "$OUT_MELEE" || true

if [ ! -s "$OUT_MELEE" ]; then
  die "No damageRoll / DR / Barrier matches written to $OUT_MELEE"
fi

echo "[*] Extract written → $OUT_MELEE"

SHA=$(sha256sum "$MELEE_FILE" | awk '{print $1}')
EVIDENCE_ID="spd-melee-$(date +%Y%m%d-%H%M%S)"
EVIDENCE_JSON="\( {EVIDENCE_DIR}/ \){EVIDENCE_ID}.json"

# Evidence JSON ohne geschachteltes Heredoc
{
  echo "{"
  echo "  \"evidence_id\": \"${EVIDENCE_ID}\","
  echo "  \"target\": \"Shattered Pixel Dungeon\","
  echo "  \"provider\": \"spd_cli\","
  echo "  \"file_path\": \"${MELEE_FILE#$HOME/}\","
  echo "  \"offset\": \"damageRoll\","
  echo "  \"sha256\": \"${SHA}\","
  echo "  \"confidence\": \"observed\","
  echo "  \"confidence_score\": 0.95,"
  echo "  \"limitation\": \"static source only; runtime Barrier/DR order residual remains\","
  echo "  \"created_at\": \"$(date -Iseconds)\""
  echo "}"
} > "$EVIDENCE_JSON"

echo "[*] Evidence written → $EVIDENCE_JSON"
echo "    sha256: $SHA"

VERIFIER="${LOGDIR}/verifier_v2.py"
if [ -f "$VERIFIER" ]; then
  echo "[*] Running verifier…"
  python3 "$VERIFIER" || die "Verifier failed"
  echo "[+] Verifier PASS"
else
  echo "[!] Verifier not found at $VERIFIER – skip (expected on first run)"
fi

echo "[+] spd_cli finished successfully"
