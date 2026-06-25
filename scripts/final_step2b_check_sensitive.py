#!/usr/bin/env python3
"""Check sensitive lines WITHOUT printing secrets"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace"), ec

# Check specific lines in llm_client.py
print("=== agent/llm_client.py lines 25-40 ===")
o, e, _ = run("sed -n '25,40p' /root/SpatialMind/agent/llm_client.py")
for line in o.split('\n'):
    print(f"  {line[:80]}")

print("\n=== test_llm.py ===")
o, e, _ = run("head -10 /root/SpatialMind/test_llm.py 2>/dev/null || echo '(not found)'")
for line in o.split('\n'):
    print(f"  {line[:80]}")

print("\n=== .env file ===")
o, e, _ = run("head -5 /root/SpatialMind/.env 2>/dev/null || echo '(no .env)'")
if o and '(no' not in o:
    for line in o.split('\n'):
        # Show variable name but mask value
        if '=' in line:
            parts = line.split('=', 1)
            print(f"  {parts[0]}=(masked)")
        else:
            print(f"  {line[:60]}")
else:
    print("  (no .env file)")

print("\n=== .env.example ===")
o, e, _ = run("cat /root/SpatialMind/.env.example 2>/dev/null || echo '(not found)'")
if o and '(not' not in o:
    print(o)
else:
    print("  (not found)")

client.close()
