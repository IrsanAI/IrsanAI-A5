ALLOWED = [
    {"id":"spd","name":"Shattered Pixel Dungeon","license":"GPLv3","why":"Baseline1, voll open source","repo":"https://github.com/00-Evan/shattered-pixel-dungeon","de":"SPD – Basis für Barrier vs DR"},
    {"id":"mindustry","name":"Mindustry","license":"GPLv3","why":"Game-Logic, Shields, perfekt für A1-A4","repo":"https://github.com/Anuken/Mindustry","de":"Mindustry – komplexe Logik"},
    {"id":"keepassdx","name":"KeePassDX","license":"GPLv3","why":"Crypto-Capa, klein","repo":"https://github.com/Kunzisoft/KeePassDX","de":"KeePassDX – Crypto-Test"},
    {"id":"uncrackable1","name":"OWASP UnCrackable L1","license":"【entity-MIT¦canonical_name=MIT】 (explicit crackme)","why":"Extra für Frida gebaut – unser A3 Live-Test","repo":"https://github.com/OWASP/owasp-mstg/tree/master/Crackmes","de":"OWASP L1 – ideal für Frida Gadget"},
    {"id":"a5crackme","name":"A5-CrackMe v1","license":"OWN / 【entity-MIT¦canonical_name=MIT】","why":"13-Byte Key A5-CrackMe!!! – eigenes Lab","path":"~/irsanai/targets/checkme.c","de":"A5 v1 – 13 Byte Key"},
    {"id":"a5crackme2","name":"A5-CrackMe v2 (PRO)","license":"OWN / 【entity-MIT¦canonical_name=MIT】","why":"20-Byte XOR + anti-debug – NEUES LEGALES TEST TARGET","path":"~/irsanai/targets/a5_crackme_v2.c","de":"A5 v2 – PRO Target 【entity-mit¦canonical_name=MIT】 XOR"},
]
BLOCKED_PATTERNS = ["whatsapp","facebook","instagram","bank","paypal","gmail","com.android.vending"]
def is_allowed(seed: str):
    s = seed.lower().strip()
    if any(p in s for p in BLOCKED_PATTERNS):
        return False, "BLOCKED: Proprietär / Missbrauchs-Risiko"
    if s.startswith("~/") or s.startswith("/data/") or s.endswith(".apk") or s.endswith(".c") or s in [a["id"] for a in ALLOWED]:
        return True, "ALLOWED"
    for a in ALLOWED:
        if a["id"] in s or a["name"].lower() in s:
            return True, f"ALLOWED: {a['name']}"
    return False, "UNKNOWN – nur Allowlist oder eigene Builds unter ~/a5_targets/"
