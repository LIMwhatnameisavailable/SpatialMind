#!/usr/bin/env python3
"""Smart fix: check current state and fix accordingly"""
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

# Check what line 874 currently looks like
import re
for m in re.finditer(r'_state.*=.*st\.session_state.*agent_state', content):
    print(f"Found at {m.start()}: {content[m.start():m.start()+80]}")

# Fix 1: already partially applied? Check both old and new patterns
old1a = '        _state = st.session_state.get("agent_state", {})'
old1b = '        _state = st.session_state.get("agent_state") or {}'
new1 = '        _state = st.session_state.get("agent_state") or {}'

if old1a in content:
    content = content.replace(old1a, new1, 1)
    print("Fix 1 applied (old pattern)")
elif old1b in content:
    print("Fix 1 already present")
else:
    print("ERROR: Cannot find _state = pattern!")
    print(content[content.find('_state'):content.find('_state')+80])

# Fix 2: check what we have around the for loop
old2a = '''        for _sn, _res in _state.get("step_results", {}).items():
            if isinstance(_res, dict):
                collected.extend(_res.get("figure_paths", []))'''

old2b = '''        _step_results = _state.get("step_results") or {}
        if isinstance(_step_results, dict):
            for _sn, _res in _step_results.items():
            if isinstance(_res, dict):
                collected.extend(_res.get("figure_paths", []))'''

new2 = '''        _step_results = _state.get("step_results") or {}
        if isinstance(_step_results, dict):
            for _sn, _res in _step_results.items():
                if isinstance(_res, dict):
                    collected.extend(_res.get("figure_paths", []))'''

if old2a in content:
    content = content.replace(old2a, new2, 1)
    print("Fix 2 applied (old pattern - full for loop)")
elif old2b in content:
    content = content.replace(old2b, new2, 1)
    print("Fix 2 applied (bad indentation - fixed)")
else:
    print("ERROR: Cannot find for-loop pattern!")
    idx = content.find("for _sn")
    if idx >= 0:
        print(content[idx:idx+250])

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

# Show lines 874-882
stdin2, stdout2, stderr2 = client.exec_command(
    "sed -n '874,882p' ~/SpatialMind/app.py", timeout=10
)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
print(f"\nLines 874-882:")
print(out2)

client.close()
print("DONE")
