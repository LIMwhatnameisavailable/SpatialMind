#!/usr/bin/env python3
"""Kill and restart Streamlit"""
import paramiko, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

channel = client.get_transport().open_session()
channel.exec_command("pkill -f 'streamlit run' 2>/dev/null; echo KILL_DONE")
channel.shutdown_write()
channel.recv_exit_status()
channel.close()
time.sleep(2)

channel2 = client.get_transport().open_session()
channel2.exec_command(
    "cd ~/SpatialMind && mkdir -p logs && nohup ~/SpatialMind/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> logs/streamlit.log 2>&1 &"
)
channel2.shutdown_write()
channel2.recv_exit_status()
channel2.close()
time.sleep(6)

stdin, stdout, stderr = client.exec_command(
    "ps aux | grep streamlit | grep -v grep | wc -l; echo '---'; tail -5 ~/SpatialMind/logs/streamlit.log",
    timeout=10
)
out = stdout.read().decode("utf-8", errors="replace").strip()
print(out)
client.close()
