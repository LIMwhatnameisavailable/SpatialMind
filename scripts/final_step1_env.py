#!/usr/bin/env python3
"""Step 1: Confirm environment and backup"""
import paramiko, os, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== Environment ===")
o, e, _ = run("cd ~/SpatialMind && pwd"); print(f"pwd: {o}")
o, e, _ = run("hostname"); print(f"hostname: {o}")
o, e, _ = run("cd ~/SpatialMind && git branch --show-current"); print(f"branch: {o}")
o, e, _ = run("cd ~/SpatialMind && git status -sb"); print(f"status:\n{o}")
o, e, _ = run("cd ~/SpatialMind && git log --oneline -5"); print(f"log:\n{o}")
o, e, _ = run("free -h"); print(f"mem:\n{o}")
o, e, _ = run("ps aux | grep -E 'streamlit' | grep -v grep || echo none"); print(f"streamlit:\n{o}")

# Backup
print("\n=== Backup ===")
backup_cmd = (
    "cd /root && tar "
    "--exclude='SpatialMind/venv' --exclude='SpatialMind/.venv' "
    "--exclude='SpatialMind/data' --exclude='SpatialMind/outputs' "
    "--exclude='SpatialMind/logs' --exclude='SpatialMind/__pycache__' "
    "--exclude='SpatialMind/**/__pycache__' "
    "-czf SpatialMind_final_working_backup_$(date +%Y%m%d_%H%M%S).tar.gz "
    "SpatialMind 2>&1"
)
o, e, _ = run(f"bash -c '{backup_cmd}'")
print(f"backup cmd result: {o[:200] if o else 'ok'} {e[:200] if e else ''}")

o, e, _ = run("ls -lh /root/SpatialMind_final_working_backup_*.tar.gz 2>/dev/null | tail -3")
print(f"backup files:\n{o if o else '(none)'}")

client.close()
print("\nStep 1 DONE")
