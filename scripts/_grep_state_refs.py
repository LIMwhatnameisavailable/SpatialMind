#!/usr/bin/env python3
"""Grep all _state and agent_state references on server app.py"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

stdin, stdout, stderr = client.exec_command(
    "grep -n '_state\\|agent_state' ~/SpatialMind/app.py", timeout=10
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
print(out)
client.close()
