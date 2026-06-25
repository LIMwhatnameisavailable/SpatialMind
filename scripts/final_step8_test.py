#!/usr/bin/env python3
"""Step 8: Light testing - verify deployment works"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== 1. HTTP Status ===")
o, e, _ = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:8501/")
print(f"  HTTP: {o}")

print("\n=== 2. systemd status ===")
o, e, _ = run("systemctl is-active spatialmind")
print(f"  Active: {o}")

print("\n=== 3. Port 8501 ===")
o, e, _ = run("ss -tlnp | grep 8501 | head -1")
print(f"  {o[:100]}")

print("\n=== 4. Journal (last 50, no-pager) ===")
o, e, _ = run("journalctl -u spatialmind -n 50 --no-pager 2>&1 | grep -iE 'error|traceback|exception|import|fail|oom|killed' | tail -5 || echo '(no errors)'")
print(f"  {o}")

print("\n=== 5. Free memory ===")
o, e, _ = run("free -h")
print(f"  {o}")

print("\n=== 6. Swap ===")
o, e, _ = run("swapon --show")
print(f"  {o}")

print("\n=== 7. git status ===")
o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"  {o}")

client.close()
print("\nStep 8 DONE")
