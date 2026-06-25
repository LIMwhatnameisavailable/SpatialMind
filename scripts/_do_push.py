#!/usr/bin/env python3
"""Test SSH connection and push to GitHub"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# 1. Test SSH
print("=== 1. SSH Test ===")
channel = client.get_transport().open_session()
channel.exec_command("ssh -o StrictHostKeyChecking=no -T git@github.com 2>&1")
import time, select
start = time.time()
while not channel.exit_status_ready():
    if time.time() - start > 15:
        break
    time.sleep(0.3)
data = b""
while channel.recv_ready():
    data += channel.recv(65536)
channel.close()
result = data.decode("utf-8", errors="replace").strip()
print(f"  {result}")

# 2. Check remote
o, e, _ = run("cd /root/SpatialMind && git remote -v")
print(f"\n=== 2. Remote ===")
print(f"  {o if o else e}")

# 3. Ensure SSH remote
o, e, _ = run("cd /root/SpatialMind && git remote get-url origin")
current_remote = o.strip()
print(f"\n=== 3. Current remote URL ===")
print(f"  {current_remote}")

if "git@github.com" not in current_remote:
    o, e, _ = run("cd /root/SpatialMind && git remote set-url origin git@github.com:LIMwhatnameisavailable/SpatialMind.git && echo 'CHANGED TO SSH'")
    print(f"  Changed: {o}")

# Verify remote
o, e, _ = run("cd /root/SpatialMind && git remote -v")
print(f"\n=== 4. Verified remote ===")
for line in o.split('\n'):
    if line.strip():
        print(f"  {line}")

# 5. Push
print(f"\n=== 5. Pushing... ===")
channel = client.get_transport().open_session()
channel.exec_command("cd /root/SpatialMind && git push origin main 2>&1")
channel.shutdown_write()

start = time.time()
out_data = ""
while not channel.exit_status_ready():
    if time.time() - start > 60:
        channel.close()
        break
    time.sleep(0.5)

while channel.recv_ready():
    out_data += channel.recv(65536).decode("utf-8", errors="replace")

ec = channel.recv_exit_status() if channel.exit_status_ready() else -1
print(f"  Result: {out_data.strip()[:500]}")
print(f"  Exit: {ec}")
channel.close()

# 6. Verify
print(f"\n=== 6. Verification ===")
o, e, _ = run("cd /root/SpatialMind && git log --oneline -1")
print(f"  Local HEAD: {o}")

o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"  Status: {o}")

# Check if origin has the commit (fetch + compare)
o, e, _ = run("cd /root/SpatialMind && git fetch origin 2>&1 && echo 'FETCH_OK'")
print(f"  Fetch: {o[:200]}")

o, e, _ = run("cd /root/SpatialMind && git log --oneline origin/main -1")
print(f"  origin/main: {o}")

# Check if 35b9d40 is in origin
o, e, _ = run("cd /root/SpatialMind && git branch -r --contains 35b9d40 2>/dev/null || echo '(not on any remote)'")
print(f"  Remote branch containing 35b9d40: {o}")

client.close()
