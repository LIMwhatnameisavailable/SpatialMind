#!/usr/bin/env python3
"""Test: invoke graph directly, dump key result fields"""
import paramiko, json

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Find a real h5ad file first
stdin, stdout, stderr = client.exec_command(
    'find /root/SpatialMind/data -name "*.h5ad" 2>/dev/null | head -3', timeout=10
)
h5ad_path = stdout.read().decode().strip().split("\n")[0]
print(f"Using h5ad: {h5ad_path}")

# Write and run test script
test_script = f'''
import sys, json, os
sys.path.insert(0, "/root/SpatialMind")
os.chdir("/root/SpatialMind")

from agent.graph import app

base = {{
    "session_id": "diag-test",
    "data_path": "{h5ad_path}",
    "data_type": "visium",
    "adata_cache_key": "session_diag_test",
    "analysis_plan": [],
    "current_step": "",
    "completed_steps": [],
    "step_params": {{
        "cluster": {{"resolution": 0.5}},
        "dimred": {{"n_pcs": 50, "n_neighbors": 15}},
        "preprocess": {{"n_top_genes": 2000}},
        "enable_nature_publish": True,
        "enable_bio_insight": True,
    }},
    "figures": {{}},
    "step_results": {{}},
    "explanations": {{}},
    "skill_outputs": {{}},
    "error_message": None,
    "retry_count": 0,
    "max_retries": 2,
    "is_complete": False,
    "request_type": "unknown",
    "messages": [],
    "output_dir": "/root/SpatialMind/outputs/figures",
}}

result = app.invoke(base, config={{{{"configurable": {{"thread_id": "diag-test"}}}}}})

# Dump key fields
print("=== KEY FIELDS ===")
print(f"request_type: {{result.get('request_type')}}")
print(f"is_complete: {{result.get('is_complete')}}")
print(f"analysis_plan: {{result.get('analysis_plan')}}")
print(f"completed_steps: {{result.get('completed_steps')}}")
print(f"error_message: {{result.get('error_message')}}")
print(f"figures: {{list(result.get('figures', {{}}).keys())}}")
print(f"step_results keys: {{list(result.get('step_results', {{}}).keys())}}")
print(f"skill_outputs keys: {{list(result.get('skill_outputs', {{}}).keys())}}")
print(f"has explanations: {{bool(result.get('explanations'))}}")

# Check step_results for figure_paths
for k, v in result.get("step_results", {{}}).items():
    if isinstance(v, dict):
        fps = v.get("figure_paths", [])
        print(f"  {{k}}: status={{v.get('status')}}, n_figures={{len(fps)}}")
        if fps:
            for fp in fps[:2]:
                print(f"    exists={{os.path.exists(fp)}}: {{fp}}")

# Check skill_outputs
for k, v in result.get("skill_outputs", {{}}).items():
    if isinstance(v, dict):
        print(f"  skill {{k}}: keys={{list(v.keys())}}")

# Check messages
msgs = result.get("messages", [])
print(f"messages: {{len(msgs)}}")
for m in msgs:
    role = m.get("role", "?")
    content = str(m.get("content", ""))[:100]
    print(f"  {{role}}: {{content}}...")

print("=== DONE ===")
'''

stdin, stdout, stderr = client.exec_command(
    'cd ~/SpatialMind && ~/SpatialMind/venv/bin/python3 -c "$(cat <<\'PYEOF\'\n' + test_script + '\nPYEOF\n)" 2>&1 | tail -80',
    timeout=600
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()
print(out)
if err: print(f"STDERR: {err[:500]}")
print(f"\nExit: {ec}")
client.close()
