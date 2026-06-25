#!/usr/bin/env python3
"""Upload local scripts/ to server and commit"""
import paramiko, os, fnmatch

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

local_scripts = r"D:\SEU\生物\计算\FINAL_project\scripts"
remote_base = "/root/SpatialMind/scripts"

# Create remote scripts dir
sftp = client.open_sftp()
try:
    sftp.stat(remote_base)
except FileNotFoundError:
    sftp.mkdir(remote_base)

# Upload all .py files from scripts/ (skip backup files)
uploaded = []
for fname in os.listdir(local_scripts):
    if not fname.endswith('.py') and not fname.endswith('.txt'):
        continue
    # Skip auto-generated or large temp files
    if fname.startswith('_ssh_helper') or 'pycache' in fname:
        continue
    local_path = os.path.join(local_scripts, fname)
    if not os.path.isfile(local_path):
        continue
    remote_path = f"{remote_base}/{fname}"
    sftp.put(local_path, remote_path)
    uploaded.append(fname)

sftp.close()
print(f"Uploaded {len(uploaded)} files to server scripts/")
for f in sorted(uploaded):
    print(f"  {f}")

# Now update README on server to mention scripts/
client.close()
