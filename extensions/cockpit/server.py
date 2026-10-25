#!/usr/bin/env python3
import http.server, json, pathlib, platform, os, sys, socketserver
from datetime import datetime, timezone
from allowlist import ALLOWED, is_allowed

ROOT = pathlib.Path(__file__).parent
REPO_ROOT = ROOT.parent.parent
EVIDENCE_DIR = pathlib.Path.home() / "a5_evidence"

def get_frida():
    try:
        import frida
        return {"installed": True, "version": getattr(frida, "__version__", "unknown"), "status": "ready"}
    except Exception as e:
        return {"installed": False, "version": None, "status": "stub", "error": str(e)[:120]}

def get_evidence():
    if not EVIDENCE_DIR.exists():
        return {"count": 0, "recent": [], "path": str(EVIDENCE_DIR)}
    files = sorted(EVIDENCE_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:8]
    recent=[]
    for f in files:
        try:
            j=json.loads(f.read_text(encoding="utf-8")[:3000])
            recent.append({"file":f.name,"eid":j.get("evidence_id"),"conf":j.get("confidence"),"prov":j.get("provider"),"mode":j.get("mode","")})
        except:
            recent.append({"file":f.name})
    return {"count": len(list(EVIDENCE_DIR.glob("*.json"))), "recent": recent, "path": str(EVIDENCE_DIR)}

def get_torwart():
    try:
        sys.path.insert(0, str(REPO_ROOT))
        import torwart.mandatory_inversion as t
        r=t.run_spd_barrier_dr_residual_i3(0)
        return {"survival":r.survival_assessment,"conf":r.overall_confidence,"residual":r.residual,"intent":r.phase0_intent,"ts":r.timestamp}
    except Exception as e:
        return {"survival":"error","conf":0,"residual":str(e)[:200]}

def get_platform():
    is_termux="com.termux" in os.environ.get("PREFIX","") or "com.termux" in os.environ.get("HOME","")
    return {"sys":platform.system(),"py":platform.python_version(),"is_termux":is_termux,"cockpit":"MOBILE" if is_termux else "DESKTOP"}

def get_metrics():
    return {"ts":datetime.now(timezone.utc).isoformat(),"platform":get_platform(),"frida":get_frida(),"evidence":get_evidence(),"torwart":get_torwart()}

def get_allowed():
    return ALLOWED

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/api/allowed":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(get_allowed()).encode()); return
        if self.path=="/api/metrics":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(get_metrics()).encode()); return
        if self.path in ("/","/index.html"): self.path="/extensions/cockpit/static/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__=="__main__":
    os.chdir(REPO_ROOT)
    import argparse; p=argparse.ArgumentParser(); p.add_argument("--port",type=int,default=8080); a=p.parse_args()
    print(f"[A5 COCKPIT] http://localhost:{a.port} -> termux-open-url http://localhost:{a.port}")
    with socketserver.TCPServer(("", a.port), H) as httpd: httpd.serve_forever()
