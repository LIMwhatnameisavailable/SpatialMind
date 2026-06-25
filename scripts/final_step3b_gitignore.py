#!/usr/bin/env python3
"""Fix .gitignore - remove overly broad patterns"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

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
*.streamlit/

# === Python ===
venv/
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# === Data ===
data/*
!data/schema/
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

# === Streamlit ===
.streamlit/
"""

sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/.gitignore", "w") as f:
    f.write(new_gitignore)
sftp.close()

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip()

o = run("cd /root/SpatialMind && git diff -- .gitignore")
print("=== git diff .gitignore ===")
print(o[:1000] if o else "(new file)")
client.close()
