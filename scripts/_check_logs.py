#!/usr/bin/env python3
"""Check latest log errors"""
import paramiko
HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)
stdin, stdout, stderr = client.exec_command("tail -80 ~/SpatialMind/logs/streamlit.log", timeout=15)
out = stdout.read().decode("utf-8", errors="replace")
# filter for errors only
for line in out.split("\n"):
    low = line.lower()
    if any(kw in low for kw in ["traceback", "error", "exception", "failed", "importerror", "keyerror", "attributeerror"]):
        print(line)
if not any(kw in line.lower() for line in out.split("\n") if any(kw in line.lower() for kw in ["traceback", "error", "exception"])):
    print("(no errors in last 80 lines)")
    print("Last 5 lines:")
    print("\n".join(out.strip().split("\n")[-5:]))
client.close()
