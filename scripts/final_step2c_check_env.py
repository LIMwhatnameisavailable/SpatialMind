#!/usr/bin/env python3
"""Find where the actual API key is configured"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

print("=== Check where API key lives ===")
o, e, _ = run("cat ~/.bashrc | grep -i ppio 2>/dev/null || echo '(none)'")
print(f"bashrc: {o[:100] if o else '(none)'}")

o, e, _ = run("cat ~/.profile | grep -i ppio 2>/dev/null || echo '(none)'")
print(f"profile: {o[:100] if o else '(none)'}")

o, e, _ = run("env | grep -i ppio 2>/dev/null || echo '(none in env)'")
print(f"env ppio: {o[:100] if o else '(none in env)'}")

o, e, _ = run("env | grep -i anthropic 2>/dev/null || echo '(none in env)'")
print(f"env anthropic: {o[:100] if o else '(none in env)'}")

o, e, _ = run("cat ~/.streamlit/secrets.toml 2>/dev/null | head -5 || echo '(none)'")
print(f"secrets: {o[:100] if o else '(none)'}")

o, e, _ = run("cat /root/SpatialMind/.streamlit/secrets.toml 2>/dev/null | head -5 || echo '(none)'")
print(f"project secrets: {o[:100] if o else '(none)'}")

# Check the nohup command
o, e, _ = run("ps aux | grep streamlit | grep -v grep | head -3")
# Show just the command structure, mask any key
cmd_line = ""
for line in o.split('\n'):
    if 'streamlit' in line:
        cmd_line = line[:50]
        break
print(f"streamlit cmd: {cmd_line}...")

client.close()
