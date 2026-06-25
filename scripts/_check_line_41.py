#!/usr/bin/env python3
"""Check llm_client.py line 41 for false positive"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

stdin, stdout, stderr = client.exec_command("sed -n '38,44p' /root/SpatialMind/agent/llm_client.py", timeout=10)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print("Lines 38-44 of llm_client.py:")
for line in out.strip().split('\n'):
    print(f"  {line}")
client.close()
