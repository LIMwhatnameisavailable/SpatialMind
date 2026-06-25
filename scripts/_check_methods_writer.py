#!/usr/bin/env python3
"""Check the problematic code in methods_writer.py and skill_invoker.py"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "cat -n ~/SpatialMind/skills/nature_publish/methods_writer.py | head -60",
    "cat -n ~/SpatialMind/agent/nodes/skill_invoker.py | head -120",
]
for c in cmds:
    stdin, stdout, stderr = client.exec_command(c, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f"$ {c[:50]}...")
    print(out)
    if err: print(f"ERR: {err}")
    print("---")
client.close()
