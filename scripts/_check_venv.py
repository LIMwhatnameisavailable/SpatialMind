#!/usr/bin/env python3
"""Check venv contents on server"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    ". ~/SpatialMind/venv/bin/activate && pip list 2>&1 | grep -iE 'langgraph|langchain|anthropic|scanpy'",
    ". ~/SpatialMind/venv/bin/activate && python -c 'import langgraph; print(f\"langgraph OK: {langgraph.__version__}\")' 2>&1",
    ". ~/SpatialMind/venv/bin/activate && python -c 'import scanpy; print(f\"scanpy OK: {scanpy.__version__}\")' 2>&1",
    ". ~/SpatialMind/venv/bin/activate && python -c 'from agent.graph import app; print(f\"graph loaded OK\")' 2>&1",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    print(f">>> {cmd}")
    if out: print(out)
    if err: print(f"ERR: {err}")
    print()

client.close()
