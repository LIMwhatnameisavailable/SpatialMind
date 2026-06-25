#!/usr/bin/env python3
"""Apply two fixes to SpatialMind's app.py on the server"""
import os
import sys

def main():
    proj = os.path.expanduser("~/SpatialMind")
    fpath = os.path.join(proj, "app.py")
    bak = fpath + ".bak_p0_qadata_$(date +%Y%m%d_%H%M%S)"

    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"Read app.py: {len(content)} chars", flush=True)

    # ── Edit 1: Remove no-data hard guard ──
    old1_start = "# ★ 校验数据路径：排除 placeholder / 不存在的路径 / 非 h5ad"
    old1_end_marker = "    }"

    idx_s = content.find(old1_start)
    if idx_s < 0:
        print("ERROR: Edit 1 start marker not found!")
        sys.exit(1)

    # Find end of the data_info block
    search_from = content.find("st.stop()", idx_s)
    if search_from < 0:
        search_from = idx_s + 100
    idx_e = content.find(old1_end_marker, search_from)
    if idx_e >= 0:
        idx_e += len(old1_end_marker)
    else:
        print("ERROR: Edit 1 end not found!")
        sys.exit(1)

    old_block = content[idx_s:idx_e]

    new_block = """# ├─ 校验数据路径：不拦截无数据请求，交给 intent_parser 路由
        # │  QA 请求无数据也可进入，analysis 无数据由 intent_parser 返回 no_data
        valid_data_path = normalize_data_path(data_path)

        # 只有确实有有效数据时才设置 data_loaded
        if valid_data_path and not st.session_state.data_loaded:
            st.session_state.data_loaded = True
            st.session_state.data_info = {
                "n_obs": "—（分析后显示）",
                "n_vars": "—（分析后显示）",
                "file_size_mb": f"{os.path.getsize(valid_data_path) / (1024 * 1024):.1f}",
            }"""

    if old_block in content:
        content = content.replace(old_block, new_block, 1)
        print("Edit 1 applied: removed no-data hard guard", flush=True)
    else:
        print("ERROR: old_block not found in content!")
        print(f"old_block start: {old_block[:100]}")
        print(f"old_block end: {old_block[-50:]}")
        sys.exit(1)

    # ── Edit 2: Figure gallery fallback in Tab 2 ──
    old2_marker = 'fig_groups: dict[str, list[dict]] = {}'
    idx2 = content.find(old2_marker)
    if idx2 < 0:
        print("ERROR: Edit 2 marker not found!")
        sys.exit(1)

    old2_start = content.rfind("# 扫描当前选中目录", 0, idx2)
    if old2_start < 0:
        old2_start = idx2

    # Find end: after st.caption line
    after_cap = content.find("st.caption(", idx2)
    if after_cap >= 0:
        cap_end = content.find("\n", after_cap)
        old2_end = content.find("\n", cap_end + 1)
        if old2_end < 0:
            old2_end = cap_end + 1
    else:
        old2_end = idx2 + 800

    old_block2 = content[old2_start:old2_end]

    new_block2 = """        # ── 收集图表文件（三级 fallback） ──
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
                    _Root.glob("*.png"),
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

        st.caption(f"\U0001f4c1 {_source_label}  ·  {sum(len(v) for v in fig_groups.values())} 张图\")"""

    if old_block2 in content:
        content = content.replace(old_block2, new_block2, 1)
        print("Edit 2 applied: figure gallery fallback", flush=True)
    else:
        print("ERROR: old_block2 not found!")
        print(f"old_block2 start: {old_block2[:100]}")
        print(f"old_block2 end: {old_block2[-50:]}")

    # ── Write ──
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Written: {os.path.getsize(fpath)} bytes", flush=True)

    # ── Syntax check ──
    ret = os.system(f"python3 -m py_compile {fpath}")
    if ret == 0:
        print("Syntax check: OK", flush=True)
    else:
        print("SYNTAX ERROR!", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
