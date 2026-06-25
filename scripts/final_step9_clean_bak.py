#!/usr/bin/env python3
"""Clean .bak files and finalize git status"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# Delete all .bak files
o, e, _ = run("cd /root/SpatialMind && find . -name '*.bak' -type f -delete && echo 'bak files deleted'")
print(f"  {o}")

# Also delete .bak* files
o, e, _ = run("cd /root/SpatialMind && find . -name '*.bak*' -type f -delete && echo 'done'")
print(f"  {o}")

# Remove backup tar.gz from home
o, e, _ = run("rm -f /root/SpatialMind_final_working_backup_*.tar.gz && echo 'backup tarball cleaned'")
print(f"  {o}")

# Final git status
o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"\n=== git status ===")
print(f"  {o}")

# List all modified/untracked files
o, e, _ = run("cd /root/SpatialMind && git status --short")
print(f"\n=== All changes ===")
for line in o.split('\n'):
    if line.strip():
        print(f"  {line}")

client.close()
print("\nCleanup DONE")
