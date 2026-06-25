#!/usr/bin/env python3
"""Generate SSH key and try push via SSH"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# Check if SSH key exists
o, e, _ = run("ls -la ~/.ssh/id_* 2>/dev/null || echo '(no keys)'")
print(f"Keys: {o[:200]}")

# Generate SSH key if needed
o, e, _ = run("ls ~/.ssh/id_ed25519.pub 2>/dev/null && echo 'exists' || (ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N '' -q && echo 'generated')")
print(f"Keygen: {o}")

# Read public key
o, e, _ = run("cat ~/.ssh/id_ed25519.pub 2>/dev/null || echo '(no pub key)'")
print(f"\n=== Public SSH Key (add to GitHub) ===")
print(f"\033[1;33m{o}\033[0m")
print(f"\nAdd this key to: https://github.com/settings/ssh/new")

# Switch remote to SSH
o, e, _ = run("cd /root/SpatialMind && git remote set-url origin git@github.com:LIMwhatnameisavailable/SpatialMind.git && echo 'SSH remote set'")
print(f"\nRemote: {o}")

# Test SSH connection
client.close()
