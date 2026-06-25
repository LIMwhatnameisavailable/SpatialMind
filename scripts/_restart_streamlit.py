#!/usr/bin/env python3
"""Restart Streamlit on server"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

cmds = [
    "pkill -f 'streamlit run' 2>/dev/null; echo KILL_DONE",
    "sleep 2",
    "mkdir -p ~/SpatialMind/logs",
    "cd ~/SpatialMind && nohup ~/SpatialMind/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> ~/SpatialMind/logs/streamlit.log 2>&1 &",
    "echo 'Streamlit started, waiting...'",
    "sleep 5",
    "tail -30 ~/SpatialMind/logs/streamlit.log",
]

full_cmd = "; ".join(cmds)
stdin, stdout, stderr = client.exec_command(full_cmd, timeout=60)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()
print(out)
if err:
    print("STDERR:", err[:500])
print("Exit:", exit_code)

# Check if running
stdin2, stdout2, stderr2 = client.exec_command("ps aux | grep 'streamlit' | grep -v grep | head -3", timeout=10)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
print("\n=== Streamlit processes ===")
print(out2 if out2 else "(none)")

client.close()
