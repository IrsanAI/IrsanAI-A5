# torwart/targets/spd.py – SPD-spezifische Logik, aus Core ausgelagert (Le Chat Kritik #3)
PKG = "com.shatteredpixel.shatteredpixeldungeon"
FINDING_ID = "spd_barrier_dr_order"

def is_valid_target_file(path):
    txt = path.read_text(errors='ignore')
    if len(txt) < 5000: return False
    if "drRoll" not in txt: return False
    if "defenseProc" not in txt: return False
    if "Barrier" not in txt and "ShieldBuff" not in txt: return False
    if "a5_targets" not in str(path): return False
    return True

def validate_observed(obs):
    if not obs.get("barrier_absorb_value"): return False, "no barrier_absorb_value"
    if obs.get("order") != "dr_before_barrier": return False, f"wrong order {obs.get('order')}"
    if "Barrier" not in (obs.get("barrier_class") or ""): return False, "barrier_class not Barrier"
    if not obs.get("attack_id"): return False, "no attack_id"
    return True, "ok"
