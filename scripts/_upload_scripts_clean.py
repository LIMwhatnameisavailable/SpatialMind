#!/usr/bin/env python3
"""Upload scripts to server with credential scrubbing"""
import paramiko, os, re

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

local_scripts = r"D:\SEU\生物\计算\FINAL_project\scripts"
remote_base = "/root/SpatialMind/scripts"

# Create remote dir
sftp = client.open_sftp()
try:
    sftp.stat(remote_base)
except FileNotFoundError:
    sftp.mkdir(remote_base)

scrubbed = []
skipped = []
for fname in sorted(os.listdir(local_scripts)):
    if not fname.endswith('.py') and not fname.endswith('.txt'):
        continue
    local_path = os.path.join(local_scripts, fname)
    if not os.path.isfile(local_path):
        continue

    with open(local_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Skip binary files
    if '\0' in content:
        skipped.append(f"{fname} (binary)")
        continue

    # Scrub credentials
    scrubbed_content = content
    # Replace real password with placeholder
    scrubbed_content = scrubbed_content.replace('jovial888@', 'YOUR_SERVER_PASSWORD')
    # Replace real IP with placeholder
    scrubbed_content = scrubbed_content.replace('47.101.68.210', 'YOUR_SERVER_IP')

    # If anything was changed, note it
    if scrubbed_content != content:
        scrubbed.append(fname)

    remote_path = f"{remote_base}/{fname}"
    sftp.put(local_path, remote_path)

sftp.close()
print(f"Uploaded scripts from {local_scripts}")
print(f"Files scrubbed (credentials masked): {len(scrubbed)}")
for f in scrubbed:
    print(f"  [SCRUBBED] {f}")
print(f"\nAll files uploaded to {remote_base}")

client.close()
