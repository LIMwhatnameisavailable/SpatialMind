#!/usr/bin/env python3
"""Check log tail and grep for errors"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "grep -inE 'traceback|error|exception|importerr|keyerr|attribute|fail|critical' ~/SpatialMind/logs/streamlit.log | tail -20",
    "sed -n '1100,1168p' ~/SpatialMind/logs/streamlit.log",
    "tail -3 ~/SpatialMind/logs/streamlit.log",
    "gtail -3 ~/SpatialMind/logs/streamlit.log 2>/dev/null || python3 -c \"import sys; lines=open('/root/SpatialMind/logs/streamlit.log').readlines(); print(''.join(lines[-10:]))\"",
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
