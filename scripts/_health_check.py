#!/usr/bin/env python3
"""Final health check"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8501/",
    "grep -c 'st.stop()' ~/SpatialMind/app.py",
    "grep -c 'fallback' ~/SpatialMind/app.py",
    "grep '^\\s*valid_data_path = normal' ~/SpatialMind/app.py",
    "ps aux | grep streamlit | grep -v grep | wc -l",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f"$ {cmd}")
    print(f"  => {out}")
    if err: print(f"  !! {err}")
    print()
client.close()
