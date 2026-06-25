#!/usr/bin/env python3
"""Verify patched app.py on server"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "grep -n '校验数据路径' ~/SpatialMind/app.py | head -5",
    "grep -n '三级 fallback' ~/SpatialMind/app.py | head -10",
    "grep -c 'st.stop()' ~/SpatialMind/app.py",
    "grep -c 'figure_paths' ~/SpatialMind/app.py",
    "grep -n 'st.stop' ~/SpatialMind/app.py",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f">>> {cmd}")
    if out:
        print(out)
    if err:
        print(f"ERR: {err}")
    print()

client.close()
