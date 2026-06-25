#!/usr/bin/env python3
"""Check plot_style.py for _infer_step_from_filename"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "grep -n '_infer_step\\|get_step_name\\|get_step_display\\|def get_figure_meta' ~/SpatialMind/tools/plot_style.py | head -20",
    "grep -n 'def ' ~/SpatialMind/tools/plot_style.py | head -30",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f"$ {cmd}")
    print(out)
    if err: print(f"ERR: {err}")
    print()

client.close()
