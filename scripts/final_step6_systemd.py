#!/usr/bin/env python3
"""Step 6: Configure systemd service and restart"""
import paramiko, time

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip(), stderr.read().decode("utf-8", errors="replace").strip(), ec

# Verify streamlit path
o, e, _ = run("ls -lh /root/SpatialMind/venv/bin/streamlit")
print(f"streamlit path: {o[:80]}...")

# Write systemd service file
service_content = """[Unit]
Description=SpatialMind Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/SpatialMind
Environment="PATH=/root/SpatialMind/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/root/SpatialMind/venv/bin/streamlit run /root/SpatialMind/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5
MemoryMax=2800M
MemoryHigh=2400M
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
"""

# Write via temp file then mv
sftp = client.open_sftp()
with sftp.open("/tmp/spatialmind.service", "w") as f:
    f.write(service_content)
sftp.close()

o, e, _ = run("cp /tmp/spatialmind.service /etc/systemd/system/spatialmind.service")
print(f"Copy service file: {e if e else 'ok'}")

o, e, _ = run("systemctl daemon-reload")
print(f"daemon-reload: {e if e else 'ok'}")

o, e, _ = run("systemctl enable spatialmind")
print(f"enable: {e if e else 'ok'}")

# Kill any existing streamlit processes (nohup ones)
o, e, _ = run("pkill -f 'streamlit run' 2>/dev/null; sleep 1; echo 'killed old'")
print(f"kill old: {o[:50]}")

time.sleep(2)

# Start via systemd
o, e, _ = run("systemctl restart spatialmind")
print(f"restart: {e if e else 'ok'}")

time.sleep(6)

# Check status
o, e, _ = run("systemctl status spatialmind --no-pager 2>&1 | head -20")
print(f"\n=== systemctl status ===")
print(o)

# Check port
o, e, _ = run("ss -tlnp | grep 8501 || echo 'NOT LISTENING'")
print(f"\n=== Port 8501 ===")
print(o[:200])

# Check journal for errors
o, e, _ = run("journalctl -u spatialmind -n 30 --no-pager 2>&1 | grep -iE 'error|traceback|exception|import|fail' | tail -10 || echo '(no errors in last 30 lines)'")
print(f"\n=== Journal errors ===")
print(o[:500])

client.close()
print("\nStep 6 DONE")
