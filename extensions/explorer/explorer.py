#!/usr/bin/env python3
"""A5 Pro Explorer – evidence.db -> HTML graph (minimal, Termux-ready)"""
import sqlite3, json, os, pathlib
db = pathlib.Path.home() / "a5_evidence" / "evidence.db"
if not db.exists():
    print(f"[!] Keine DB: {db} – erst evidence sammeln")
    exit(0)
con = sqlite3.connect(db)
cur = con.cursor()
rows = cur.execute("SELECT evidence_id, diagnosis_id, confidence, observed FROM evidence LIMIT 100").fetchall()
print(f"[+] {len(rows)} Evidence Rows")
# Minimal HTML
html = "<html><body><h1>A5 Evidence Graph</h1><ul>"
for eid, did, conf, obs in rows:
    html += f"<li>{eid} -> {did} | {conf} | {obs}</li>"
html += "</ul></body></html>"
out = pathlib.Path("explorer.html")
out.write_text(html)
print(f"[+] Wrote {out.resolve()}")
