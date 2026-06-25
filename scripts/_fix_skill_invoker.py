#!/usr/bin/env python3
"""Fix skill_invoker.py: change except ImportError to except Exception"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Read skill_invoker.py
sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/agent/nodes/skill_invoker.py", "rb") as f:
    content = f.read().decode("utf-8")
sftp.close()
print(f"Read: {len(content)} bytes, lines: {content.count(chr(10))}")

# Fix: except ImportError -> except Exception (line 69)
old = "    except ImportError as e:"
new = "    except Exception as e:"

assert old in content, f"Pattern not found! Searching..."
idx = content.find("except ImportError")
print(f"Found at index {idx}: {content[idx:idx+50]}")

content = content.replace(old, new, 1)

# Verify fix
assert "except ImportError" not in content, "Fix didn't apply!"
assert old not in content, "Old pattern still present!"
print("Fix applied: ImportError -> Exception")

# Upload
sftp2 = client.open_sftp()
with sftp2.open("/root/SpatialMind/agent/nodes/skill_invoker.py", "wb") as f:
    f.write(content.encode("utf-8"))
sftp2.close()

# Syntax check
stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -m py_compile agent/nodes/skill_invoker.py && echo SYNTAX_OK",
    timeout=10
)
ec = stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"Syntax: {out}")
if err: print(f"ERR: {err}")

# Verify the line
stdin2, stdout2, stderr2 = client.exec_command(
    "grep -n 'except' ~/SpatialMind/agent/nodes/skill_invoker.py", timeout=10
)
out2 = stdout2.read().decode("utf-8", errors="replace").strip()
print(f"\nExcept lines:")
print(out2)

client.close()
print("DONE")
