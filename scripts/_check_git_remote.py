#!/usr/bin/env python3
"""Check git remote and SSH config for GitHub push"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== Git Remote ===")
o, e, _ = run("cd /root/SpatialMind && git remote -v")
print(o)

print("\n=== SSH Config ===")
o, e, _ = run("cat ~/.ssh/config 2>/dev/null || echo '(no config)'")
print(o[:200])

print("\n=== SSH Keys ===")
o, e, _ = run("ls -la ~/.ssh/ 2>/dev/null || echo '(no .ssh)'")
print(o[:300])

print("\n=== Git User ===")
o, e, _ = run("cd /root/SpatialMind && git config user.name && git config user.email")
print(o)

client.close()
