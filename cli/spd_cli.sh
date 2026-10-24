#!/data/data/com.termux/files/usr/bin/bash
set -e
BASE=~/shattered-pixel-dungeon
LOGDIR=~/spd_logs
[ -d "$LOGDIR" ] || mkdir -p "$LOGDIR"
find "$BASE/core" -name "MeleeWeapon.java" -exec grep -n "damageRoll" -A 5 {} \; > "$LOGDIR/melee.txt"
python3 "$LOGDIR/verifier_v2.py"
