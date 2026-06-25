#!/usr/bin/env python3
"""Test route on server: QA must not be blocked, no_data must work"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

TEST_SCRIPT = r"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "SpatialMind"))
from agent.graph import app

base = {
    "session_id": "route-p0",
    "data_path": "",
    "data_type": "unknown",
    "adata_cache_key": "session_route_p0",
    "analysis_plan": [],
    "current_step": "",
    "completed_steps": [],
    "step_params": {},
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
}

def run(text):
    s = dict(base)
    s["user_input"] = text
    r = app.invoke(s, config={"configurable": {"thread_id": "route-p0-" + text[:4]}})
    print("=" * 60)
    print(text)
    print("request_type:", r.get("request_type"))
    print("analysis_plan:", r.get("analysis_plan"))
    print("is_complete:", r.get("is_complete"))
    msgs = [m for m in r.get("messages", []) if m.get("role") == "assistant"]
    print("assistant:", msgs[-1]["content"][:120] if msgs else "")

run("什么是转录组？")
run("什么是空间转录组？")
run("执行完整分析")
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Write test script to server
sftp = client.open_sftp()
with sftp.open("/tmp/test_route_p0.py", "w") as f:
    f.write(TEST_SCRIPT)
sftp.close()

# Run it
stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && python3 /tmp/test_route_p0.py 2>&1", timeout=120
)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()

print(out)
if err:
    print("STDERR:", err)
print("Exit:", exit_code)
client.close()
