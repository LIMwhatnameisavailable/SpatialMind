#!/usr/bin/env python3
"""Run quick analysis with test data and dump result state"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

test_code = '''
import sys, json
from pathlib import Path
sys.path.insert(0, "/root/SpatialMind")
from agent.graph import app
from agent.state import get_initial_state

# Find any .h5ad file on the server
h5ad_files = list(Path("/root/SpatialMind/data").rglob("*.h5ad"))
if not h5ad_files:
    h5ad_files = list(Path("/root/SpatialMind/data/uploads").rglob("*.h5ad"))
print(f"Found h5ad: {h5ad_files[0] if h5ad_files else 'NONE'}")

initial = get_initial_state(
    user_input="Please load data then perform full analysis (QC, preprocessing, dimred, clustering, spatial, marker genes)",
    data_path=str(h5ad_files[0]),
    data_type="visium",
    step_params={"cluster": {"resolution": 0.5}, "dimred": {"n_pcs": 50}, "preprocess": {"n_top_genes": 2000}},
    session_id="test-diag-001",
    output_dir="/root/SpatialMind/outputs/figures",
)

result = app.invoke(initial, config={"configurable": {"thread_id": "test-diag-001"}})

print(f"request_type: {result.get('request_type')}")
print(f"is_complete: {result.get('is_complete')}")
print(f"analysis_plan: {result.get('analysis_plan')}")
print(f"completed_steps: {result.get('completed_steps')}")
print(f"current_step: {result.get('current_step')}")
print(f"error_message: {result.get('error_message')}")
print(f"figures count: {len(result.get('figures', {}))}")
step_results = result.get("step_results", {})
print(f"step_results keys: {list(step_results.keys())}")
for k, v in step_results.items():
    if isinstance(v, dict):
        print(f"  {k}: status={v.get('status')}, has_summary={'summary' in v}")
        fps = v.get('figure_paths', [])
        if fps: print(f"    figure_paths: {fps[:2]}")
'''

stdin, stdout, stderr = client.exec_command(
    'cd ~/SpatialMind && ~/SpatialMind/venv/bin/python3 -c "' + test_code.replace('"', '\\"') + '" 2>&1',
    timeout=300
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()
print(out)
if err: print("STDERR:", err[:1000])
print(f"\nExit: {ec}")
client.close()
