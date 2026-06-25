#!/usr/bin/env python3
"""Clean remaining temp files"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode("utf-8", errors="replace").strip()

print("=== Remove temp/debug files ===")
for f in [
    "/root/SpatialMind/test_llm.py",
    "/root/SpatialMind/scripts",
    "/root/SpatialMind/_ssh_helper.py",
    "/root/SpatialMind/_diag_b_output.txt",
    "/root/SpatialMind/_diag_output.txt",
    "/root/SpatialMind/_diag_executor.txt",
    "/root/SpatialMind/_server_hotfix_plot_style_append.py",
]:
    o = run(f"rm -rf {f} 2>/dev/null && echo 'removed {f}' || echo 'not found {f}'")
    if o: print(f"  {o}")

print("\n=== Check remaining stray files ===")
o = run("ls -la /root/SpatialMind/_*.py /root/SpatialMind/_*.txt /root/SpatialMind/_*.sh 2>/dev/null || echo '(none)'")
print(f"  {o}")

client.close()
