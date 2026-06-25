"""SSH helper for SpatialMind server"""
import paramiko
import sys

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"


def safe_out(msg):
    """Print with encoding fallback for Windows GBK console"""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            print(msg.encode('utf-8', errors='replace').decode('gbk', errors='replace'))
        except Exception:
            print("(output omitted - encoding error)")


def run_commands(commands, description="", timeout=30):
    """Run commands on server and return output"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, USER, PASSWORD, timeout=15)
        results = []
        if description:
            safe_out(f"\n{'='*60}")
            safe_out(f"  {description}")
            safe_out(f"{'='*60}")
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8', errors='replace').strip()
            err = stderr.read().decode('utf-8', errors='replace').strip()
            results.append((cmd, out, err, exit_code))
        return results
    except Exception as e:
        safe_out(f"SSH Error: {e}")
        return None
    finally:
        client.close()


def run_script_raw(script_content, description="", timeout=60):
    """Run a multi-line script on server, return raw bytes (no decode)"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, USER, PASSWORD, timeout=15)
        if description:
            safe_out(f"\n{'='*60}")
            safe_out(f"  {description}")
            safe_out(f"{'='*60}")
        stdin, stdout, stderr = client.exec_command("bash -s", timeout=timeout)
        stdin.write(script_content)
        stdin.flush()
        stdin.channel.shutdown_write()
        exit_code = stdout.channel.recv_exit_status()
        out_bytes = stdout.read()
        err_bytes = stderr.read()
        return out_bytes, err_bytes, exit_code
    except Exception as e:
        safe_out(f"SSH Error: {e}")
        return b"", str(e).encode(), -1
    finally:
        client.close()


def run_script(script_content, description="", timeout=60):
    """Run a multi-line script on server, return decoded strings"""
    out_bytes, err_bytes, exit_code = run_script_raw(script_content, description, timeout)
    out = out_bytes.decode('utf-8', errors='replace').strip() if out_bytes else ""
    err = err_bytes.decode('utf-8', errors='replace').strip() if err_bytes else ""
    return out, err, exit_code


def fetch_text_from_server(cmd, description="", timeout=30):
    """
    Run a command and save output to a local UTF-8 file.
    Returns the local file path or None on failure.
    """
    import tempfile
    import os
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, USER, PASSWORD, timeout=15)
        if description:
            safe_out(f"\n{'='*60}")
            safe_out(f"  {description}")
            safe_out(f"{'='*60}")
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        raw = stdout.read()
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb")
        tf.write(raw)
        tf.close()
        return tf.name
    except Exception as e:
        safe_out(f"SSH Error: {e}")
        return None
    finally:
        client.close()