#!/usr/bin/env python3
"""Run diag_invoke.py on server via SFTP upload then simple ssh exec"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Script is already uploaded to /tmp/diag_invoke.py from previous step

# Run - simple one-liner
transport = client.get_transport()
channel = transport.open_session()
channel.exec_command("cd /root/SpatialMind && /root/SpatialMind/venv/bin/python3 /tmp/diag_invoke.py '/root/SpatialMind/data/uploads/GSM9046244_Embryo_E7.5_stereo_rep2.h5ad' 2>&1")
channel.shutdown_write()

import time
start = time.time()
buf = []
while True:
    if channel.exit_status_ready():
        break
    if time.time() - start > 540:
        print("TIMEOUT after 9 min")
        channel.close()
        break
    time.sleep(1)

if channel.recv_ready():
    data = channel.recv(65536).decode("utf-8", errors="replace")
    buf.append(data)

# Wait a bit more for any remaining data
time.sleep(2)
while channel.recv_ready():
    data = channel.recv(65536).decode("utf-8", errors="replace")
    buf.append(data)

ec = channel.recv_exit_status()
output = "".join(buf)
lines = output.strip().split("\n")
print("\n".join(lines[-60:]))
print(f"\nExit: {ec}")
client.close()
