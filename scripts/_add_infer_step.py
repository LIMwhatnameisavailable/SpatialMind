#!/usr/bin/env python3
"""Add _infer_step_from_filename to plot_style.py"""
import paramiko

HOST = "47.101.68.210"; PORT = 22; USER = "root"; PASSWORD = "jovial888@"
client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

# Read plot_style.py
sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/tools/plot_style.py", "rb") as f:
    content = f.read().decode("utf-8")
sftp.close()
print(f"Read: {len(content)} bytes")

# Check if function already exists
if "_infer_step_from_filename" in content:
    print("Function already exists, no changes needed")
else:
    # Find insertion point: before manage_session_figures or after get_step_display_name
    # Line 222 (after get_step_display_name, before manage_session_figures)
    insert_point = "def manage_session_figures"
    idx = content.find(insert_point)
    if idx < 0:
        print("ERROR: Cannot find insertion point")
        client.close()
        exit(1)

    new_func = """
def _infer_step_from_filename(filename: str) -> str:
    \"\"\"从图片文件名推断步骤名\"\"\"
    fname = filename.lower()
    step_map = {
        "qc": "qc",
        "preprocess": "preprocess",
        "pca": "dimred",
        "umap": "dimred",
        "dimred": "dimred",
        "cluster": "cluster",
        "leiden": "cluster",
        "louvain": "cluster",
        "spatial": "spatial",
        "marker": "marker",
        "deg": "marker",
        "svg": "svg",
        "data_load": "data_load",
        "data_loader": "data_load",
    }
    for key, step in step_map.items():
        if key in fname:
            return step
    return "other"


"""

    content = content[:idx] + new_func + content[idx:]
    print(f"Inserted function: {len(new_func)} bytes")

    # Upload
    sftp2 = client.open_sftp()
    with sftp2.open("/root/SpatialMind/tools/plot_style.py", "wb") as f:
        f.write(content.encode("utf-8"))
    sftp2.close()
    print(f"Uploaded: {len(content)} bytes")

    # Syntax check
    stdin, stdout, stderr = client.exec_command(
        "cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -m py_compile tools/plot_style.py && echo SYNTAX_OK",
        timeout=10
    )
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"Syntax: {out}")
    if err: print(f"ERR: {err}")

    # Verify
    stdin2, stdout2, stderr2 = client.exec_command(
        "grep -n '_infer_step' ~/SpatialMind/tools/plot_style.py", timeout=10
    )
    out2 = stdout2.read().decode("utf-8", errors="replace").strip()
    print(f"\n_grep:_infer_step:\n{out2}")

client.close()
print("DONE")
