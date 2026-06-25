#!/usr/bin/env python3
"""Step 3: Update .gitignore"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip()

# Read current .gitignore
current = run("cat /root/SpatialMind/.gitignore 2>/dev/null || echo '(empty)'")
print("=== Current .gitignore ===")
print(current[:500])

# Write new .gitignore with all needed patterns
new_gitignore = """# === Env & Secrets ===
.env
.env.*
!.env.example
server_ssh.env
*.pem
*.key
*password*
*secret*
*token*

# === Python ===
venv/
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# === Data ===
data/
*.h5ad
*.h5
*.loom
*.h5seurat

# === Outputs & Logs ===
outputs/
logs/

# === OS ===
.DS_Store
Thumbs.db

# === IDE ===
.vscode/
.idea/

# === Temp / Diagnostic ===
_tmp/
_tmp_*/
_*.py
_*.txt
_*.sh
!/scripts/
!/skills/
!/tools/
!/agent/
!/tests/
!.gitignore
!.env.example
!README.md

# === Streamlit ===
.streamlit/
"""

# Write it
sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/.gitignore", "w") as f:
    f.write(new_gitignore)
sftp.close()

# Verify
o = run("cd /root/SpatialMind && git diff -- .gitignore")
print(f"\n=== git diff .gitignore ===")
print(o[:1000] if o else "(no changes tracked, fully new file)")

client.close()
print("\nStep 3 DONE")
