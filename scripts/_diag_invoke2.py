#!/usr/bin/env python3
"""Write test script to server and run it"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# First find h5ad
stdin, stdout, stderr = client.exec_command('find /root/SpatialMind/data -name "*.h5ad" 2>/dev/null | head -3', timeout=10)
h5ad_path = stdout.read().decode().strip().split("\n")[0]
print(f"h5ad: {h5ad_path}")

# Write test script to server
test_script = '''#!/root/SpatialMind/venv/bin/python3
import sys, os, json
sys.path.insert(0, "/root/SpatialMind")
os.chdir("/root/SpatialMind")

from agent.graph import app

h5ad_path = sys.argv[1]
print(f"Using: {h5ad_path}")

base = {
    "session_id": "diag-test",
    "data_path": h5ad_path,
    "data_type": "visium",
    "adata_cache_key": "session_diag_test",
    "analysis_plan": [],
    "current_step": "",
    "completed_steps": [],
    "step_params": {
        "cluster": {"resolution": 0.5},
        "dimred": {"n_pcs": 50, "n_neighbors": 15},
        "preprocess": {"n_top_genes": 2000},
        "enable_nature_publish": False,
        "enable_bio_insight": False,
    },
    "figures": {},
    "step_results": {},
    "explanations": {},
    "skill_outputs": {},
    "error_message": None,
    "retry_count": 0,
    "max_retries": 2,
    "is_complete": False,
    "request_type": "unknown",
    "messages": [],
    "output_dir": "/root/SpatialMind/outputs/figures",
}

result = app.invoke(base, config={"configurable": {"thread_id": "diag-test"}})

print("=== KEY FIELDS ===")
print(json.dumps({
    "request_type": result.get("request_type"),
    "is_complete": result.get("is_complete"),
    "analysis_plan": result.get("analysis_plan"),
    "completed_steps": result.get("completed_steps"),
    "error_message": result.get("error_message"),
    "n_figures": len(result.get("figures", {})),
    "step_results_keys": list(result.get("step_results", {}).keys()),
    "skill_outputs_keys": list(result.get("skill_outputs", {}).keys()),
}, indent=2))

# Check step_results for figure_paths
for k, v in result.get("step_results", {}).items():
    if isinstance(v, dict):
        fps = v.get("figure_paths", [])
        print(f"  {k}: status={v.get('status')}, n_figs={len(fps)}")
        if fps:
            for fp in fps[:2]:
                print(f"    exists={os.path.exists(fp)}: {fp}")

# Check messages last 2
msgs = result.get("messages", [])
print(f"messages: {len(msgs)}")
for m in msgs[-2:]:
    print(f"  {m.get('role')}: {str(m.get('content',''))[:150]}")

print("=== DONE ===")
'''

sftp = client.open_sftp()
with sftp.open("/tmp/diag_invoke.py", "w") as f:
    f.write(test_script)
sftp.close()

# Run
stdin, stdout, stderr = client.exec_command(
    f"cd ~/SpatialMind && {h5ad_path} && /tmp/diag_invoke.py '{h5ad_path}' 2>&1 | tail -50",
    timeout=600
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()
print(out)
if err: print(f"ERR: {err[:500]}")
print(f"\nExit: {ec}")
client.close()
