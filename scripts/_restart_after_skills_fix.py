#!/usr/bin/env python3
"""Restart Streamlit on server"""
import paramiko, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Kill old
ch = client.get_transport().open_session()
ch.exec_command("pkill -f 'streamlit run' 2>/dev/null; sleep 2; echo KILL_DONE")
ch.shutdown_write(); ch.recv_exit_status(); ch.close()

# Start new
ch = client.get_transport().open_session()
ch.exec_command("cd ~/SpatialMind && nohup ~/SpatialMind/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> logs/streamlit.log 2>&1 &")
ch.shutdown_write(); ch.recv_exit_status(); ch.close()
time.sleep(6)

# Verify
stdin, stdout, stderr = client.exec_command("ps aux | grep streamlit | grep -v grep | wc -l; echo 'PORT:'; ss -tlnp | grep 8501", timeout=10)
print(stdout.read().decode())
client.close()
