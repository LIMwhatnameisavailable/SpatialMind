#!/usr/bin/env python3
"""Fix methods_writer.py to handle non-dict step_results"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/skills/nature_publish/methods_writer.py", "rb") as f:
    content = f.read().decode("utf-8")
sftp.close()
print(f"Read: {len(content)} bytes")

# The issue: for step, result in step_results.items(): result might be str
# Fix: wrap the .get() calls in isinstance check
old = """    # 收集分析细节
    methods_summary = []
    for step, result in step_results.items():
        metrics = result.get("metrics", {})
        params = step_params.get(step, {})
        summary = result.get("summary", "")"""

new = """    # 收集分析细节
    methods_summary = []
    for step, result in step_results.items():
        if not isinstance(result, dict):
            methods_summary.append(f"{step}: (result not available)")
            continue
        metrics = result.get("metrics", {})
        params = step_params.get(step, {})
        summary = result.get("summary", "")"""

assert old in content, "Old pattern not found!"
content = content.replace(old, new, 1)

sftp2 = client.open_sftp()
with sftp2.open("/root/SpatialMind/skills/nature_publish/methods_writer.py", "wb") as f:
    f.write(content.encode("utf-8"))
sftp2.close()

stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -m py_compile skills/nature_publish/methods_writer.py && echo SYNTAX_OK",
    timeout=10
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"Syntax: {out}")
if err: print(f"ERR: {err}")

client.close()
print("DONE")
