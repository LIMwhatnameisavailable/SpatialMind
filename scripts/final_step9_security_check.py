#!/usr/bin/env python3
"""Step 9: Security check & GitHub commit"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== Final Security Check ===")

# 1. Check no .env or sensitive files tracked
o, e, _ = run(
    "cd /root/SpatialMind && git ls-files | grep -Ei "
    "'(^|/)(\\.env|server_ssh|.*password.*|.*secret.*|.*token.*|\\.pem|\\.key)$' || echo '(clean)'"
)
print(f"Tracked sensitive: {o}")

# 2. Check for real secrets in code (not placeholders)
o, e, _ = run(
    "cd /root/SpatialMind && grep -RInE "
    "'(PPIO_API_KEY|ANTHROPIC_API_KEY|sk-[a-zA-Z0-9])=' "
    "--exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv "
    "--exclude-dir=data --exclude-dir=outputs --exclude-dir=logs "
    "--exclude-dir=scripts . 2>/dev/null || echo '(no real keys in code)'"
)
lines = [l for l in o.split('\n') if l.strip() and 'your_api_key' not in l]
if lines:
    print("WARNING - Real secrets found!")
    for l in lines:
        print(f"  {l.split(':')[0]}:{l.split(':')[1]}: (value hidden)")
else:
    print(f"Secrets check: clean")

# 3. Check .gitignore covers all sensitive paths
o, e, _ = run("cat /root/SpatialMind/.gitignore")
print(f"\nFinal .gitignore:")
for line in o.split('\n'):
    if line.strip() and not line.startswith('#'):
        print(f"  {line}")

print("\n=== Ready for commit ===")
o, e, _ = run("cd /root/SpatialMind && git status -sb")
print(f"  {o}")

client.close()
