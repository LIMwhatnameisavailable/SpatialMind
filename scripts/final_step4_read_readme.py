#!/usr/bin/env python3
"""Step 4: Read current README and llm_client to prepare README update"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace")

# Read llm_client for env var names
o = run("sed -n '1,60p' /root/SpatialMind/agent/llm_client.py")
print("=== llm_client.py env reads ===")
for line in o.split('\n'):
    if 'os.getenv' in line or 'st.secrets' in line or 'environ[' in line:
        print(f"  {line.strip()}")

# Read current README size
o = run("wc -c /root/SpatialMind/README.md 2>/dev/null || echo '(none)'")
print(f"\nREADME size: {o.strip()}")

# Check git diff for README
o = run("cd /root/SpatialMind && git diff -- README.md | head -10 || echo '(unchanged)'")
print(f"\nCurrent README diff: {o.strip()[:200]}")

client.close()
