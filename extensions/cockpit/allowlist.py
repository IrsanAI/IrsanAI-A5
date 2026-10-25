# A5 Pro – Legal Seed Allowlist (kein Binary, nur Namen + Checks)
ALLOWED = [
    {"id":"spd","name":"Shattered Pixel Dungeon","license":"GPLv3","why":"Baseline1, voll open source","path":"~/spd-src/","repo":"https://github.com/00-Evan/shattered-pixel-dungeon"},
    {"id":"mindustry","name":"Mindustry","license":"GPLv3","why":"Game-Logic, Shields, perfekt für A1-A4","repo":"https://github.com/Anuken/Mindustry"},
    {"id":"keepassdx","name":"KeePassDX","license":"GPLv3","why":"Crypto-Capa, klein","repo":"https://github.com/Kunzisoft/KeePassDX"},
    {"id":"uncrackable1","name":"OWASP UnCrackable L1","license":"MIT (explicit crackme)","why":"Extra für Frida gebaut – unser A3 Live-Test","repo":"https://github.com/OWASP/owasp-mstg/tree/master/Crackmes"},
    {"id":"a5crackme","name":"A5-CrackMe v1 (checkme.c)","license":"OWN / A5","why":"13-Byte Key A5-CrackMe!!! – eigenes Lab","path":"~/irsanai/targets/checkme.c"},
]

BLOCKED_PATTERNS = ["whatsapp","facebook","instagram","bank","paypal","gmail","com.android.vending"]

def is_allowed(seed: str):
    s = seed.lower().strip()
    if any(p in s for p in BLOCKED_PATTERNS):
        return False, "BLOCKED: Proprietär / Missbrauchs-Risiko – nur eigene oder explizit erlaubte Open-Source Targets"
    # eigene Datei unter HOME ist ok, wenn User bestätigt dass es seins ist
    if s.startswith("~/") or s.startswith("/data/") or s.endswith(".apk") or s.endswith(".c"):
        return True, "OWN FILE – nur wenn du Owner bist oder GPL/MIT Lizenz hast. Wird mit Consent geloggt."
    for a in ALLOWED:
        if a["id"] in s or a["name"].lower() in s:
            return True, f"ALLOWED: {a['name']} – {a['license']} – {a['why']}"
    return False, "UNKNOWN – nicht in Allowlist. Bitte nur Targets aus der Liste unten oder eigene Builds unter ~/a5_targets/ nutzen."
