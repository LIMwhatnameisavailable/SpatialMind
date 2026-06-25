#!/usr/bin/env python3
"""Dig into server logs to find where analysis output went"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# 1. Check log lines 400-900 - the deprecation warnings are at start and end, analysis should be middle
# 2. Check if there's another log file
# 3. Check streamlit process stderr redirect

cmds = [
    # Check non-warning lines in lines 400-900 (where analysis output should be)
    r"python3 -c $'import sys\nlines = open(\"/root/SpatialMind/logs/streamlit.log\").readlines()\nfor i,l in enumerate(lines[400:900], 401):\n    if \"use_container_width\" not in l and \"Please replace\" not in l:\n        print(f\"{i}: {l}\", end=\"\")'",
    # Check if there are any error lines
    "grep -cin 'traceback\\|error\\|exception' ~/SpatialMind/logs/streamlit.log",
    # Check streamlit process environment
    "cat /proc/33862/environ 2>/dev/null | tr '\\0' '\\n' | grep -i log || echo no proc",
    # Check if nohup.out exists with output
    "cat ~/SpatialMind/nohup.out 2>/dev/null | tail -20 || echo no nohup.out",
    # Check streamlit config
    "cat ~/.streamlit/config.toml 2>/dev/null | head -20 || echo no streamlit config",
]
for c in cmds:
    stdin, stdout, stderr = client.exec_command(c, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f">>> {c[:60]}...")
    if out: print(out[:2000])
    if err: print(f"ERR: {err}")
    print()
client.close()
