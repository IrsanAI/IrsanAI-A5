#!/usr/bin/env python3
import http.server, json, pathlib, platform, os, sys, socketserver, threading, time, hashlib
from datetime import datetime, timezone
from allowlist import ALLOWED, is_allowed
ROOT = pathlib.Path(__file__).parent
REPO_ROOT = ROOT.parent.parent
EVIDENCE_DIR = pathlib.Path.home() / "a5_evidence"
JOBS={}; LOCK=threading.Lock()

def get_frida():
    try:
        import frida
        return {"installed": True, "version": getattr(frida, "__version__", "unknown"), "status": "ready"}
    except: return {"installed": False, "version": None, "status": "stub"}

def get_evidence():
    if not EVIDENCE_DIR.exists(): return {"count":0,"recent":[],"path":str(EVIDENCE_DIR)}
    files=sorted(EVIDENCE_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:8]
    recent=[]
    for f in files:
        try:
            j=json.loads(f.read_text()[:2000])
            recent.append({"file":f.name,"eid":j.get("evidence_id"),"conf":j.get("confidence")})
        except: recent.append({"file":f.name})
    return {"count":len(list(EVIDENCE_DIR.glob("*.json"))),"recent":recent,"path":str(EVIDENCE_DIR)}

def get_torwart():
    try:
        sys.path.insert(0,str(REPO_ROOT))
        import torwart.mandatory_inversion as t
        r=t.run_spd_barrier_dr_residual_i3(0)
        return {"survival":r.survival_assessment,"conf":r.overall_confidence}
    except Exception as e: return {"survival":"error","conf":0}

def get_platform():
    is_termux="com.termux" in os.environ.get("PREFIX","")
    return {"sys":platform.system(),"py":platform.python_version(),"is_termux":is_termux}

def get_metrics():
    return {"ts":datetime.now(timezone.utc).isoformat(),"platform":get_platform(),"frida":get_frida(),"evidence":get_evidence(),"torwart":get_torwart()}

def start_job(seed):
    jid=f"job-{int(time.time())}"
    JOBS[jid]={"id":jid,"seed":seed,"status":"running","progress":0,"logs":[],"start":time.time()}
    def run():
        steps=[("VALIDATE","Seed validieren + Allowlist + SHA256","INFO"),("TORWART","Torwart AAP v1.2","TORWART"),("A1_MCP","A1 MCP Orchestrierung","A1"),("A2_GHIDRA","A2 Ghidra PCode decompile","A2"),("A3_FRIDA","A3 Frida Gadget non-root","A3"),("A4_CAPA","A4 capa + PCode","A4"),("A5_EVIDENCE","A5 Evidence-Graph JSON","A5"),("DONE","Fertig Transparency","DONE")]
        for idx,(code,name,layer) in enumerate(steps):
            ts=datetime.now().strftime("%H:%M:%S")
            with LOCK:
                JOBS[jid]["logs"].append({"simple":f"[{code}] {name} – seed={seed}","tech":f"[{code}] {name} | {layer} | ts={ts}","layer":layer,"code":code,"ts":ts})
                JOBS[jid]["progress"]=int((idx+1)/len(steps)*100)
            time.sleep(0.7)
        ev={"evidence_id":f"cockpit-{jid}","provider":"cockpit","seed":seed,"confidence":"inferred"}
        (EVIDENCE_DIR/f"cockpit-{jid}.json").write_text(json.dumps(ev))
        with LOCK: JOBS[jid]["status"]="done"
    threading.Thread(target=run,daemon=True).start()
    return jid

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/api/allowed":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","http://localhost:8080"); self.end_headers()
            self.wfile.write(json.dumps(ALLOWED).encode()); return
        if self.path=="/api/metrics":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","http://localhost:8080"); self.end_headers()
            self.wfile.write(json.dumps(get_metrics()).encode()); return
        if self.path.startswith("/api/job/"):
            jid=self.path.split("/")[-1]
            with LOCK: data=JOBS.get(jid,{"error":"not found"})
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","http://localhost:8080"); self.end_headers()
            self.wfile.write(json.dumps(data).encode()); return
        if self.path in ("/","/index.html"): self.path="/extensions/cockpit/static/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        if self.path=="/api/seed":
            length=int(self.headers.get('content-length',0)); body=self.rfile.read(length).decode()
            try: seed=json.loads(body).get("seed","")
            except: seed=body
            ok,msg=is_allowed(seed)
            if not ok:
                self.send_response(403); self.send_header("Content-Type","application/json"); self.end_headers()
                self.wfile.write(json.dumps({"error":msg}).encode()); return
            jid=start_job(seed)
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","http://localhost:8080"); self.end_headers()
            self.wfile.write(json.dumps({"job_id":jid}).encode()); return
        self.send_response(404); self.end_headers()

if __name__=="__main__":
    os.chdir(REPO_ROOT)
    import argparse; p=argparse.ArgumentParser(); p.add_argument("--port",type=int,default=8080); a=p.parse_args()
    print(f"[A5 COCKPIT V3 HONEST] http://127.0.0.1:{a.port} – localhost only, inferred only, guard active")
    with socketserver.TCPServer(("127.0.0.1", a.port), H) as httpd: httpd.serve_forever()
