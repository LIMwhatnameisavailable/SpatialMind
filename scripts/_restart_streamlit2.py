#!/usr/bin/env python3
"""Kill old Streamlit and start fresh one"""
import paramiko
import time

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Kill old
stdin, stdout, stderr = client.exec_command(
    "pkill -f 'streamlit run' 2>/dev/null; echo KILL_DONE; sleep 1; ps aux | grep streamlit | grep -v grep",
    timeout=15
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()
if out: print("After kill:", out)
if err: print("ERR:", err[:300])

# Start fresh - use nohup properly with exec_command running in background
channel = client.get_transport().open_session()
channel.exec_command(
    "cd ~/SpatialMind && mkdir -p logs && nohup ~/SpatialMind/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> logs/streamlit.log 2>&1 &"
)
channel.shutdown_write()
exit_code = channel.recv_exit_status()
print(f"Start command exit: {exit_code}")
channel.close()

time.sleep(6)

# Check
stdin2, stdout2, stderr2 = client.exec_command(
    "ps aux | grep 'streamlit' | grep -v grep; echo '---'; tail -20 ~/SpatialMind/logs/streamlit.log",
    timeout=15
)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
err2 = stderr2.read().decode("utf-8", errors="replace").strip()
print("=== Streamlit status ===")
print(out2)
if err2: print("ERR:", err2[:300])

# Check if port is listening
stdin3, stdout3, stderr3 = client.exec_command("ss -tlnp | grep 8501", timeout=10)
out3 = stdout3.read().decode("utf-8", errors="replace").strip()
print("\n=== Port 8501 ===")
print(out3 if out3 else "(not listening)")

client.close()
