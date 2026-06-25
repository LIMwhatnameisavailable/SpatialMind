#!/usr/bin/env python3
"""Step 7: Configure 2G swap"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# Check current swap
o, e, _ = run("swapon --show 2>/dev/null || echo '(no swap)'")
print(f"Current swap: {o}")
o, e, _ = run("free -h")
print(f"Memory: {o}")

# Create swap
o, e, _ = run("fallocate -l 2G /swapfile 2>&1")
print(f"\nCreate swapfile: {o[:100] if o else 'ok'} {e[:100] if e else ''}")

o, e, _ = run("chmod 600 /swapfile && mkswap /swapfile 2>&1 | tail -3")
print(f"Format: {o[:100] if o else ''} {e[:100] if e else ''}")

o, e, _ = run("swapon /swapfile 2>&1")
print(f"Enable: {o[:100] if o else 'ok'} {e[:100] if e else ''}")

# Add to fstab
o, e, _ = run("grep -q '/swapfile' /etc/fstab && echo 'already in fstab' || (echo '/swapfile none swap sw 0 0' >> /etc/fstab && echo 'added to fstab')")
print(f"fstab: {o[:100]}")

# Verify
o, e, _ = run("swapon --show")
print(f"\n=== Swap status ===")
print(o)
o, e, _ = run("free -h")
print(f"free -h:")
print(o)

client.close()
print("\nStep 7 DONE")
