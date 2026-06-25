#!/usr/bin/env python3
"""Quick analysis: check figure session dirs and verify analysis output files"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Check a few simple things
def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip()

# Check session figure dirs
print("=== Session dirs ===")
print(run("find ~/SpatialMind/outputs/figures -type d 2>/dev/null"))

# Check env file is loaded
print("\n=== .env keys ===")
print(run("grep -v '^#' ~/SpatialMind/.env 2>/dev/null | grep '=' | head -5 || echo no .env"))

# Check streamlit process env
print("\n=== Check memory ===")
print(run("free -m | head -3"))

# Check if analysis output files exist (step_results etc)
print("\n=== outputs/ reports ===")
print(run("ls ~/SpatialMind/outputs/reports/ 2>/dev/null; echo '---'; ls ~/SpatialMind/outputs/exports/ 2>/dev/null"))

# Check if stderr went somewhere else
print("\n=== journalctl ===")
print(run("journalctl -u streamlit* --no-pager -n 5 2>/dev/null || echo no journalctl"))

client.close()
