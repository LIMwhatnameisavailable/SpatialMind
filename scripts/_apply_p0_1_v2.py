#!/usr/bin/env python3
"""Reapply P0.1 fix with correct indentation"""
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

# Fix 1: _state None guard
old1 = '        _state = st.session_state.get("agent_state", {})'
new1 = '        _state = st.session_state.get("agent_state") or {}'
assert old1 in content, "old1 not found!"
content = content.replace(old1, new1, 1)
print("Fix 1 applied: _state None guard")

# Fix 2: step_results safe iteration - include the for-loop body
old2 = '''        for _sn, _res in _state.get("step_results", {}).items():
            if isinstance(_res, dict):
                collected.extend(_res.get("figure_paths", []))'''

new2 = '''        _step_results = _state.get("step_results") or {}
        if isinstance(_step_results, dict):
            for _sn, _res in _step_results.items():
                if isinstance(_res, dict):
                    collected.extend(_res.get("figure_paths", []))'''

assert old2 in content, f"old2 not found! content around it:\n{content[content.find('for _sn'):content.find('for _sn')+200]}"
content = content.replace(old2, new2, 1)
print("Fix 2 applied: step_results safe iteration")

# Upload
sftp2 = client.open_sftp()
with sftp2.open("/root/SpatialMind/app.py", "wb") as f:
    f.write(content.encode("utf-8"))
sftp2.close()
print(f"Uploaded: {len(content)} bytes")

# Syntax check
stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -m py_compile app.py && echo SYNTAX_OK 2>&1",
    timeout=10
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"Syntax: {out}")
if err: print(f"ERR: {err}")

# Show fixed lines
stdin2, stdout2, stderr2 = client.exec_command(
    "sed -n '874,882p' ~/SpatialMind/app.py", timeout=10
)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
print(f"\nLines 874-882:")
print(out2)

client.close()
print("DONE")
