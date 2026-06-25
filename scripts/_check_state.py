#!/usr/bin/env python3
"""Check server state after user's run"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "ps aux | grep streamlit | grep -v grep",
    "ss -tlnp | grep 8501",
    "ls -la ~/SpatialMind/logs/",
    "wc -l ~/SpatialMind/logs/streamlit.log",
    "grep -n '20:3' ~/SpatialMind/logs/streamlit.log | head -20",
    "ls -lt ~/SpatialMind/outputs/figures/*.png 2>/dev/null | head -10",
    "ls -lt ~/SpatialMind/outputs/figures/ 2>/dev/null | head -10",
]
for c in cmds:
    stdin, stdout, stderr = client.exec_command(c, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f">>> {c}")
    if out: print(out)
    if err: print(f"ERR: {err}")
    print()
client.close()
