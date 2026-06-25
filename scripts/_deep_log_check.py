#!/usr/bin/env python3
"""Deep log inspection - look for all analysis output"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Check if log has ANY output between 20:27 and 20:31 that's not deprecation warnings
cmds = [
    "python3 -c \"
import re
lines = open('/root/SpatialMind/logs/streamlit.log').readlines()
# Filter out use_container_width lines
anal = [l for l in lines if 'use_container_width' not in l and 'Please replace' not in l]
print(f'Total: {len(lines)}, Non-warning: {len(anal)}')
for l in anal[-30:]:
    print(l.rstrip())
\"",
    "ls -la ~/SpatialMind/outputs/figures/*.png 2>/dev/null",
    "ls -la ~/SpatialMind/outputs/figures/session_*/ 2>/dev/null | head -20",
    "cat ~/SpatialMind/outputs/checkpoints.db 2>/dev/null | head -5; ls -la ~/SpatialMind/outputs/checkpoints.db 2>/dev/null",
]
for c in cmds:
    stdin, stdout, stderr = client.exec_command(c, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f">>> {c}")
    if out: print(out[:2000])
    if err: print(f"ERR: {err}")
    print()
client.close()
