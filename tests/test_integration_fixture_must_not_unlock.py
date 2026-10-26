"""Integration: fixture darf nie 0.88 unlocken, selbst mit echtem Hash+Nonce"""
import pathlib, subprocess, json, time, sys
ev_dir=pathlib.Path.home()/ "a5_evidence"
for f in ev_dir.glob("spd_barrier*.json"): f.unlink(missing_ok=True)
for f in ev_dir.glob(".frida_session_*"): f.unlink(missing_ok=True)
# fixture run
subprocess.run([sys.executable, "providers/a3_spd_live_run.py", "--fixture"], check=True)
from torwart.mandatory_inversion import count_real_observed
cnt=count_real_observed()
print(f"after fixture count={cnt} expected 0")
assert cnt==0, f"fixture must not unlock 0.88, got {cnt}"
# cleanup
for f in ev_dir.glob("spd_barrier*.json"): f.unlink(missing_ok=True)
print("PASS integration fixture must stay 0.72")
