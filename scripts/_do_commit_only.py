#!/usr/bin/env python3
"""Commit only (no push - will be done locally)"""
import paramiko, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# git add
o, e, _ = run("cd /root/SpatialMind && git add .gitignore README.md .env.example agent/nodes/skill_invoker.py app.py skills/nature_publish/methods_writer.py tools/plot_style.py 2>&1")
print(f"add: {o[:100] if o else 'ok'} {e[:100] if e else ''}")

# git rm test_llm.py
o, e, _ = run("cd /root/SpatialMind && git rm --cached test_llm.py 2>&1 || git rm test_llm.py 2>&1 || echo '(not tracked)')")
print(f"rm: {o[:100] if e else 'ok'}")

# Status
o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"status: {o}")

# Commit (no push)
channel = client.get_transport().open_session()
channel.exec_command(
    'cd /root/SpatialMind && git commit -m "fix: complete P0 routing, None guard, skill_invoker exception, figure fallback; docs: README, .gitignore, .env.example; deploy: systemd, swap" 2>&1'
)
channel.shutdown_write()

# Wait for completion with shorter timeout
import select
start = time.time()
while not channel.exit_status_ready():
    if time.time() - start > 20:
        channel.close()
        break
    time.sleep(0.5)

if channel.recv_ready():
    data = channel.recv(65536).decode("utf-8", errors="replace")
    print(f"commit: {data[:300]}")
ec = channel.recv_exit_status() if channel.exit_status_ready() else -1
print(f"exit: {ec}")
channel.close()

# Latest commit hash
o, e, _ = run("cd /root/SpatialMind && git log --oneline -1")
print(f"latest: {o}")

client.close()
