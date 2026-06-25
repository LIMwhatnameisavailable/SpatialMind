#!/usr/bin/env python3
"""Fix P0.1: _state None guard on line 874"""
import os
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Read current app.py
sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/app.py", "rb") as f:
    content = f.read().decode("utf-8")
sftp.close()

print(f"Read: {len(content)} bytes")

# Fix line 874: _state = st.session_state.get("agent_state", {})
# Change to: _state = st.session_state.get("agent_state") or {}
old = '        _state = st.session_state.get("agent_state", {})'
new = '        _state = st.session_state.get("agent_state") or {}'

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed _state None guard")
else:
    print("WARNING: pattern not found!")
    # Try to find it
    idx = content.find("agent_state")
    if idx >= 0:
        print(f"Found 'agent_state' at {idx}, context: {content[idx-20:idx+80]}")

# Also add extra safety: wrap the step_results iteration with None guard
# Find the _state iteration block
old2 = '''        for _sn, _res in _state.get("step_results", {}).items():'''
new2 = '''        _step_results = _state.get("step_results") or {}
        if isinstance(_step_results, dict):
            for _sn, _res in _step_results.items():'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Fixed step_results safe iteration")
else:
    print(f"WARNING: old2 pattern not found!")
    idx2 = content.find("step_results")
    if idx2 >= 0:
        print(f"Found 'step_results' at {idx2}: {content[idx2-10:idx2+80]}")

# Syntax check
with open("/tmp/_app_p0_1.py", "w", encoding="utf-8") as f:
    f.write(content)

import subprocess
ret = subprocess.run(
    [r"D:\SEU\生物\计算\FINAL_project\_server_python", "-c", "import py_compile; py_compile.compile(r'D:\SEU\生物\计算\FINAL_project\_server_app.py')"],
    capture_output=True, text=True, shell=True
)
# Can't do local syntax check. Do it on server.

# Upload
sftp2 = client.open_sftp()
with sftp2.open("/root/SpatialMind/app.py", "wb") as f:
    f.write(content.encode("utf-8"))
sftp2.close()
print(f"Uploaded: {len(content)} bytes")

# Syntax check
stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -m py_compile app.py && echo SYNTAX_OK",
    timeout=10
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"Syntax: {out}")
if err: print(f"ERR: {err}")

# Verify the fix
stdin2, stdout2, stderr2 = client.exec_command(
    "sed -n '874,878p' ~/SpatialMind/app.py", timeout=10
)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
print(f"\nLine 874-878:")
print(out2)

client.close()
