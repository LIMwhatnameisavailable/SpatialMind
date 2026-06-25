#!/usr/bin/env python3
"""Check git credentials and try push"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# Check credential helper
o, e, _ = run("git config --global credential.helper 2>/dev/null || echo '(none)'")
print(f"credential helper: {o}")

# Check if credential cache has github token
o, e, _ = run("git config --global --list 2>/dev/null | grep -i cred || echo '(no cred config)'")
print(f"cred config: {o}")

# Try a simple push test - dry run
print("\n=== Trying git add + commit (dry) ===")

# First, check what files will be committed
o, e, _ = run(
    "cd /root/SpatialMind && git add --dry-run "
    ".gitignore README.md .env.example "
    "agent/nodes/skill_invoker.py app.py "
    "skills/nature_publish/methods_writer.py "
    "tools/plot_style.py 2>&1"
)
print(f"add dry-run:\n{o}")

# Check if test_llm.py deletion needs separate handling
o, e, _ = run("cd /root/SpatialMind && git status test_llm.py")
print(f"\ntest_llm.py status: {o[:100]}")

client.close()
