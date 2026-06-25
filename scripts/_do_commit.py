#!/usr/bin/env python3
"""Commit on server, note for user about push"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# git add
o, e, _ = run(
    "cd /root/SpatialMind && git add "
    ".gitignore README.md .env.example "
    "agent/nodes/skill_invoker.py app.py "
    "skills/nature_publish/methods_writer.py "
    "tools/plot_style.py && "
    "git rm test_llm.py 2>/dev/null; "
    "echo 'ADD_OK'"
)
print(f"git add: {o[:200]}")

# git status after add
o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"\nAfter add:\n{o}")

# Commit
o, e, _ = run(
    "cd /root/SpatialMind && git commit -m "
    "\"fix: complete P0 routing, None guard, skill_invoker exception handling, figure fallback; docs: rewrite README, update .gitignore, fix .env.example; deploy: systemd service, 2G swap\" "
    "2>&1"
)
print(f"\nCommit:")
print(f"  {o[:300]}")
if e:
    print(f"  STDERR: {e[:200]}")

# Try push (might fail, that's OK)
o, e, _ = run("cd /root/SpatialMind && git push origin main 2>&1")
print(f"\nPush result:")
if 'fatal' in o.lower() or (e and 'fatal' in e.lower()):
    print(f"  Push failed (no credentials) - user needs to push from local")
    print(f"  Error: {(o+e)[:300]}")
elif '->' in o:
    print(f"  Push successful!")
    print(f"  {o[:500]}")
else:
    print(f"  {o[:200]}")
    if e: print(f"  {e[:200]}")

# Get commit hash
o, e, _ = run("cd /root/SpatialMind && git log --oneline -1")
print(f"\nLatest commit: {o[:80]}")

client.close()
