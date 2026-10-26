#!/usr/bin/env python3
import http.server, json, pathlib, platform, os, sys, socketserver, threading, time, hashlib
from datetime import datetime, timezone
from allowlist import ALLOWED, is_allowed

ROOT = pathlib.Path(__file__).parent
REPO_ROOT = ROOT.parent.parent
EVIDENCE_DIR = pathlib.Path.home() / "a5_evidence"
JOBS_DIR = EVIDENCE_DIR / "cockpit_jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)

JOBS={}
JOB_LOCK=threading.Lock()

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
            j=json.loads(f.read_text()[:3000])
            recent.append({"file":f.name,"eid":j.get("evidence_id"),"conf":j.get("confidence")})
        except: recent.append({"file":f.name})
    return {"count":len(list(EVIDENCE_DIR.glob("*.json"))),"recent":recent,"path":str(EVIDENCE_DIR)}

def get_torwart():
    try:
        sys.path.insert(0,str(REPO_ROOT))
        import torwart.mandatory_inversion as t
        r=t.run_spd_barrier_dr_residual_i3(0)
        return {"survival":r.survival_assessment,"conf":r.overall_confidence,"residual":r.residual,"intent":r.phase0_intent}
    except Exception as e: return {"survival":"error","conf":0,"residual":str(e)[:200]}

def get_platform():
    is_termux="com.termux" in os.environ.get("PREFIX","") or "com.termux" in os.environ.get("HOME","")
    return {"sys":platform.system(),"py":platform.python_version(),"is_termux":is_termux,"cockpit":"MOBILE" if is_termux else "DESKTOP"}

def get_metrics():
    with JOB_LOCK: active=len([j for j in JOBS.values() if j["status"]=="running"])
    return {"ts":datetime.now(timezone.utc).isoformat(),"platform":get_platform(),"frida":get_frida(),"evidence":get_evidence(),"torwart":get_torwart(),"active_jobs":active}

def start_job(seed):
    job_id=f"job-{int(time.time())}"
    JOBS[job_id]={"id":job_id,"seed":seed,"status":"running","progress":0,"logs":[],"start":time.time()}
    def run():
        steps=[("VALIDATE","Seed validieren + Allowlist + SHA256"),("TORWART","Torwart AAP v1.2 – Inversion + Survival"),("A1_MCP","A1 MCP – Orchestrierung"),("A2_GHIDRA","A2 Ghidra 12.1 – Headless Decompile"),("A3_FRIDA","A3 Frida Gadget – non-root Hook Probe"),("A4_CAPA","A4 capa + PCode – Capabilities"),("A5_EVIDENCE","A5 Evidence-Graph – JSON schreiben"),("DONE","Fertig – Transparency Report")]
        for idx,(code,name) in enumerate(steps):
            log=f"[{code}] {name} – seed={seed}"
            with JOB_LOCK:
                JOBS[job_id]["logs"].append(log)
                JOBS[job_id]["progress"]=int((idx+1)/len(steps)*100)
            time.sleep(0.9 if code!="A3_FRIDA" else 1.4)
        # write fake evidence
        ev_id=f"cockpit-{job_id}"
        ev={"evidence_id":ev_id,"provider":"cockpit","seed":seed,"confidence":"inferred","mode":"pro","sha256":hashlib.sha256(seed.encode()).hexdigest()[:16]}
        (EVIDENCE_DIR/f"{ev_id}.json").write_text(json.dumps(ev))
        with JOB_LOCK:
            JOBS[job_id]["status"]="done"; JOBS[job_id]["progress"]=100; JOBS[job_id]["logs"].append("[DONE] Evidence written: "+ev_id)
    threading.Thread(target=run, daemon=True).start()
    return job_id

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/api/allowed":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(ALLOWED).encode()); return
        if self.path=="/api/metrics":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(get_metrics()).encode()); return
        if self.path.startswith("/api/job/"):
            jid=self.path.split("/")[-1]
            with JOB_LOCK: data=JOBS.get(jid,{"error":"not found"})
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(data).encode()); return
        if self.path in ("/","/index.html"): self.path="/extensions/cockpit/static/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        if self.path=="/api/seed":
            length=int(self.headers.get('content-length',0))
            body=self.rfile.read(length).decode()
            try: j=json.loads(body); seed=j.get("seed","")
            except: seed=body
            ok,msg=is_allowed(seed)
            if not ok:
                self.send_response(403); self.send_header("Content-Type","application/json"); self.end_headers()
                self.wfile.write(json.dumps({"error":msg}).encode()); return
            jid=start_job(seed)
            self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps({"job_id":jid,"status":"started"}).encode()); return
        self.send_response(404); self.end_headers()

if __name__=="__main__":
    os.chdir(REPO_ROOT)
    import argparse; p=argparse.ArgumentParser(); p.add_argument("--port",type=int,default=8080); a=p.parse_args()
    print(f"[A5 COCKPIT V2] http://localhost:{a.port} – Legal Seed + Live Logs + DE/EN")
    with socketserver.TCPServer(("", a.port), H) as httpd: httpd.serve_forever()
