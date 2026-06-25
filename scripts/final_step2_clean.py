#!/usr/bin/env python3
"""Step 2: Clean sensitive info and temp files"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== Remove temp scripts ===")
cmds = [
    "cd ~/SpatialMind && rm -f _check_methods_writer.py test_agent.py test_spatialmind_agent.py",
    "rm -f /tmp/test_skill_safe.py /tmp/test_route_only.py /tmp/test_route_p0.py /tmp/diag_v3.py /tmp/diag_invoke.py",
]
for c in cmds:
    o, e, _ = run(c)
    print(f"  rm: {c[:50]}... {'ok' if not e else e[:100]}")

print("\n=== Find potentially sensitive files ===")
o, e, _ = run(
    "find /root/SpatialMind -maxdepth 4 -type f \( "
    "-name '*.env' -o -name '*ssh*' -o -name '*password*' -o "
    "-name '*secret*' -o -name '*.pem' -o -name '*.key' -o "
    "-name '*token*' \) -print 2>/dev/null"
)
print(o if o else "(none found)")

print("\n=== Check if git is tracking sensitive files ===")
o, e, _ = run("cd ~/SpatialMind && git ls-files | grep -Ei '(^|/)(\.env|server_ssh|.*password.*|.*secret.*|.*token.*|.*\.pem|.*\.key)$' || true")
print(o if o else "(none tracked)")

print("\n=== Scan code for hardcoded secrets (no values output) ===")
o, e, _ = run(
    "cd ~/SpatialMind && grep -RInE 'API_KEY|SECRET|TOKEN|PASSWORD|PPIO_API|ANTHROPIC_API|sk-[a-zA-Z0-9]|BEGIN .*PRIVATE KEY' "
    "--exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv "
    "--exclude-dir=data --exclude-dir=outputs --exclude-dir=logs "
    "--exclude-dir=scripts . 2>/dev/null || true"
)
# Check if any line contains an actual secret (not placeholder or template)
lines = [l for l in o.split('\n') if l.strip()]
sensitive_found = False
for l in lines:
    # Skip .env.example and README placeholders
    if 'your_api_key' in l or 'YOUR_API_KEY' in l or 'your_key' in l:
        continue
    # Check if it has a real-looking API key (long string after = sign)
    if 'API_KEY' in l or 'PASSWORD' in l or 'SECRET' in l or 'TOKEN' in l:
        vals = l.split('=')[-1].strip() if '=' in l else ''
        if vals and len(vals) > 20 and 'your' not in vals.lower() and 'placeholder' not in vals.lower():
            print(f"  SENSITIVE FOUND: {l.split(':')[0]}:{l.split(':')[1]} (value hidden)")
            sensitive_found = True
        else:
            continue
    # Check for sk- API keys
    if 'sk-' in l:
        vals = [p for p in l.split() if p.startswith('sk-') and len(p) > 20]
        if vals and 'sk-your' not in str(vals[0]).lower():
            print(f"  SENSITIVE FOUND: {l.split(':')[0]}:{l.split(':')[1]} (contains sk- key)")
            sensitive_found = True

if not sensitive_found:
    print("  (no real secrets found in code)")
    print(f"  (matched {len(lines)} template/placeholder lines only)")

print("\nStep 2 DONE")
client.close()
