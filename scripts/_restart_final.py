#!/usr/bin/env python3
"""Kill and restart Streamlit, no output garbling"""
import paramiko, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

channel = client.get_transport().open_session()
channel.exec_command("pkill -f 'streamlit run' 2>/dev/null; echo KILL_DONE")
channel.shutdown_write(); channel.recv_exit_status(); channel.close()

time.sleep(2)

channel = client.get_transport().open_session()
channel.exec_command("cd ~/SpatialMind && nohup ~/SpatialMind/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> logs/streamlit.log 2>&1 &")
channel.shutdown_write(); channel.recv_exit_status(); channel.close()

time.sleep(6)

stdin, stdout, stderr = client.exec_command("tail -3 ~/SpatialMind/logs/streamlit.log", timeout=10)
print(stdout.read().decode().strip())
client.close()
