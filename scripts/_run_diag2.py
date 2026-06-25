#!/usr/bin/env python3
"""Write test script to server, run it, capture output without blocking"""
import paramiko, os

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Upload the test script
script_path = os.path.join(os.path.dirname(__file__), "_diag_invoke_v3.py")
test_script = r'''#!/root/SpatialMind/venv/bin/python3
import sys, os, json
sys.path.insert(0, "/root/SpatialMind")
os.chdir("/root/SpatialMind")
from agent.graph import app

h5ad = sys.argv[1]
print("Using:", h5ad, flush=True)

s = {
    "session_id": "diag-v3", "data_path": h5ad, "data_type": "stereo",
    "adata_cache_key": "diag_v3", "analysis_plan": [], "current_step": "",
    "completed_steps": [], "step_params": {"cluster": {"resolution": 0.5},
    "dimred": {"n_pcs": 50, "n_neighbors": 15}, "preprocess": {"n_top_genes": 2000},
    "enable_nature_publish": False, "enable_bio_insight": False},
    "figures": {}, "step_results": {}, "explanations": {}, "skill_outputs": {},
    "error_message": None, "retry_count": 0, "max_retries": 2,
    "is_complete": False, "request_type": "unknown", "messages": [],
    "output_dir": "/root/SpatialMind/outputs/figures",
}
r = app.invoke(s, config={"configurable": {"thread_id": "diag-v3"}})

print("request_type:", r.get("request_type"))
print("is_complete:", r.get("is_complete"))
print("analysis_plan:", r.get("analysis_plan"))
print("completed_steps:", r.get("completed_steps"))
print("error_message:", r.get("error_message"))
print("n_figures:", len(r.get("figures", {})))
print("step_results_keys:", list(r.get("step_results", {}).keys()))
print("skill_outputs_keys:", list(r.get("skill_outputs", {}).keys()))
for k, v in r.get("step_results", {}).items():
    if isinstance(v, dict):
        fps = v.get("figure_paths", [])
        print(f"  {k}: status={v.get('status')}, n_figs={len(fps)}")
        for fp in fps[:2]:
            print(f"    exists={os.path.exists(fp)}: {fp}")
msgs = r.get("messages", [])
print("messages:", len(msgs))
for m in msgs[-2:]:
    c = str(m.get("content", ""))[:120]
    print(f"  {m.get('role')}: {c}")
print("DONE")
'''

sftp = client.open_sftp()
with sftp.open("/tmp/diag_v3.py", "w") as f:
    f.write(test_script)
sftp.close()
print("Uploaded /tmp/diag_v3.py")

# Run
stdin, stdout, stderr = client.exec_command(
    "cd /root/SpatialMind && /root/SpatialMind/venv/bin/python3 /tmp/diag_v3.py '/root/SpatialMind/data/uploads/GSM9046244_Embryo_E7.5_stereo_rep2.h5ad' 2>&1",
    timeout=540, get_pty=True
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print("\n" + "="*60)
lines = out.strip().split("\n")
for l in lines:
    print(l)
if err.strip():
    print("STDERR:", err[:500])
print(f"\nExit: {ec}")
client.close()
