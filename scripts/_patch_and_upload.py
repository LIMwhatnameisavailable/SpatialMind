#!/usr/bin/env python3
"""
Patch app.py: load from local copy, edit, upload to server.
Usage: python _patch_and_upload.py
"""
import os
import sys
import base64
import paramiko

PROJECT = "D:/SEU/生物/计算/FINAL_project"
LOCAL_COPY = os.path.join(PROJECT, "_server_app.py")

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

# ── Read ──
with open(LOCAL_COPY, "r", encoding="utf-8") as f:
    content = f.read()

print(f"Read local copy: {len(content)} chars")

# ══════════════════════════════════════
# Edit 1: Remove no-data hard guard
# ══════════════════════════════════════
old1_start = "# ★ 校验数据路径：排除 placeholder / 不存在的路径 / 非 h5ad"
idx_s = content.find(old1_start)
assert idx_s >= 0, "Edit 1 start marker not found!"

# Find the end of data_info block
idx_stop = content.find("st.stop()", idx_s)
assert idx_stop >= 0, "st.stop() not found!"
idx_e = content.find("    }", idx_stop)
assert idx_e >= 0, "data_info closing brace not found!"
idx_e += len("    }")  # include the closing brace

old_block = content[idx_s:idx_e]

new_block = '''# ├─ 校验数据路径：不再拦截无数据请求，交给 intent_parser 路由
        # │  QA 请求无数据也可进入，analysis 无数据由 intent_parser 返回 no_data
        valid_data_path = normalize_data_path(data_path)

        # 只有确实有有效数据时才设置 data_loaded
        if valid_data_path and not st.session_state.data_loaded:
            st.session_state.data_loaded = True
            st.session_state.data_info = {
                "n_obs": "—（分析后显示）",
                "n_vars": "—（分析后显示）",
                "file_size_mb": f"{os.path.getsize(valid_data_path) / (1024 * 1024):.1f}",
            }'''

assert old_block in content, "Edit 1 block not found in content!"
content = content.replace(old_block, new_block, 1)
print("Edit 1 applied: removed no-data hard guard")

# ══════════════════════════════════════
# Edit 2: Figure gallery fallback
# ══════════════════════════════════════
old2_marker = 'fig_groups: dict[str, list[dict]] = {}'
idx2 = content.find(old2_marker)
assert idx2 >= 0, "Edit 2 marker not found!"

old2_start = content.rfind("# 扫描当前选中目录", 0, idx2)
if old2_start < 0:
    old2_start = idx2

old2_after = content.find("st.caption(", idx2)
assert old2_after >= 0, "st.caption not found after fig_groups!"

old2_end = content.find("\n", old2_after)
old2_end = content.find("\n", old2_end + 1)

old_block2 = content[old2_start:old2_end]

new_block2 = '''        # ── 收集图表文件（三级 fallback） ──
        # Level 1: 优先从 agent_state.step_results 获取 figure_paths
        collected = []
        _state = st.session_state.get("agent_state", {})
        for _sn, _res in _state.get("step_results", {}).items():
            if isinstance(_res, dict):
                collected.extend(_res.get("figure_paths", []))
        # 去重 + 过滤存在文件
        _seen = set()
        figure_files = []
        for _p in collected:
            if _p not in _seen and os.path.exists(_p):
                _seen.add(_p)
                figure_files.append(_p)

        # Level 2: selected_run_path 子目录下的 png
        if not figure_files and selected_run_path and os.path.exists(selected_run_path):
            from pathlib import Path as _Path
            figure_files = sorted(
                _Path(selected_run_path).glob("*.png"),
                key=lambda p: p.stat().st_mtime, reverse=True
            )
            figure_files = [str(p) for p in figure_files]

        # Level 3: outputs/figures 根目录（最多 30 张最新）
        if not figure_files:
            _root = FIGURES_DIR
            if _root.exists():
                from pathlib import Path as _Path
                figure_files = sorted(
                    _root.glob("*.png"),
                    key=lambda p: p.stat().st_mtime, reverse=True
                )[:30]
                figure_files = [str(p) for p in figure_files]

        # 按步骤分组
        _source_label = selected_run_path or "outputs/figures/"
        fig_groups: dict[str, list[dict]] = {}
        for _fpath in figure_files:
            _fname = os.path.basename(_fpath)
            _mtime_dt = datetime.fromtimestamp(os.path.getmtime(_fpath))
            _step = get_step_name_from_filename(_fname)
            fig_groups.setdefault(_step, []).append({
                "path": _fpath,
                "filename": _fname,
                "mtime": _mtime_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "mtime_dt": _mtime_dt,
            })

        st.caption(f"\U0001f4c1 {_source_label} ·  {sum(len(v) for v in fig_groups.values())} 张图")'''

assert old_block2 in content, "Edit 2 block not found in content!"
content = content.replace(old_block2, new_block2, 1)
print("Edit 2 applied: figure gallery fallback")

# ══════════════════════════════════════
# Upload to server via paramiko
# ══════════════════════════════════════
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

sftp = client.open_sftp()
with sftp.open("/root/SpatialMind/app.py", "wb") as f:
    f.write(content.encode("utf-8"))
sftp.close()
print(f"Uploaded: {len(content)} bytes to /root/SpatialMind/app.py")

# Syntax check on server
stdin, stdout, stderr = client.exec_command(
    "cd ~/SpatialMind && python3 -m py_compile app.py && echo SYNTAX_OK", timeout=15
)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
if out: print(out)
if err: print("STDERR:", err)
print(f"Syntax check exit: {exit_code}")

# Verify file size
stdin2, stdout2, stderr2 = client.exec_command("wc -c ~/SpatialMind/app.py", timeout=15)
vc = stdout2.read().decode().strip()
print(f"Server file: {vc}")

client.close()
print("DONE")
