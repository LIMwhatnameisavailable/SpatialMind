"""
executor 节点 — 执行单步分析（不调用 LLM）

职责：
1. 从 analysis_plan 中取出下一步骤
2. 调用对应的 tool 函数
3. 更新 state 中的 figures、step_results
4. 将生成的图片路径保存到 output/figures/

工具函数映射表：
    qc         -> tools.qc.run_qc
    preprocess -> tools.preprocessing.run_preprocessing
    dimred     -> tools.dimred.run_dimred
    cluster    -> tools.clustering.run_clustering
    spatial    -> tools.spatial_viz.run_spatial_viz
    marker     -> tools.marker_genes.run_marker_analysis
    svg        -> tools.svg.run_svg
"""

import importlib
from datetime import datetime
from agent.state import AgentState

# 步骤 -> (模块路径, 函数名)
TOOL_MAP = {
    "data_load": ("tools.data_loader", "load_data"),
    "qc": ("tools.qc", "run_qc"),
    "preprocess": ("tools.preprocessing", "run_preprocessing"),
    "dimred": ("tools.dimred", "run_dimred"),
    "cluster": ("tools.clustering", "run_clustering"),
    "spatial": ("tools.spatial_viz", "run_spatial_viz"),
    "marker": ("tools.marker_genes", "run_marker_analysis"),
    "svg": ("tools.svg", "run_svg"),
}


def executor_node(state: AgentState) -> dict:
    """执行分析计划中的下一个步骤"""
    analysis_plan = state.get("analysis_plan", [])
    completed_steps = state.get("completed_steps", [])
    step_params = state.get("step_params", {})
    adata_cache_key = state.get("adata_cache_key", "")

    # 找到下一个未完成的步骤
    next_step = None
    for step in analysis_plan:
        if step not in completed_steps:
            next_step = step
            break

    if next_step is None:
        return {"is_complete": True, "current_step": ""}

    # 检查工具是否存在
    if next_step not in TOOL_MAP:
        return {
            "error_message": f"未知步骤: {next_step}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # 动态导入并调用工具函数
    module_path, func_name = TOOL_MAP[next_step]
    try:
        module = importlib.import_module(module_path)
        tool_func = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        return {
            "error_message": f"加载工具 {next_step} 失败: {e}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # 获取该步骤的参数
    params = step_params.get(next_step, {})

    # 执行工具
    try:
        # 特殊处理 data_load：需额外传入 data_path
        if next_step == "data_load":
            data_path = state.get("data_path", "")
            result = tool_func(adata_key_or_path=adata_cache_key, file_path=data_path)
        else:
            result = tool_func(adata_key=adata_cache_key, **params)
    except Exception as e:
        return {
            "error_message": f"执行 {next_step} 时出错: {e}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # 处理结果
    if result.get("status") == "error":
        return {
            "error_message": f"{next_step} 执行失败: {result.get('error', '未知错误')}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # 成功 —— 更新 state
    figures = dict(state.get("figures", {}))
    step_results = dict(state.get("step_results", {}))

    figure_paths = result.get("figure_paths", [])
    if figure_paths:
        figures[next_step] = figure_paths[-1]  # 保存最后一张图为主图

    step_results[next_step] = {
        "summary": result.get("summary", ""),
        "metrics": result.get("metrics", {}),
        "figure_paths": figure_paths,
        "timestamp": datetime.now().isoformat(),
    }

    updated_figures = dict(state.get("figures", {}))
    if figure_paths:
        updated_figures[next_step] = figure_paths[-1]

    return {
        "current_step": next_step,
        "completed_steps": completed_steps + [next_step],
        "figures": updated_figures,
        "step_results": step_results,
        "retry_count": 0,  # 重置重试计数
        "error_message": None,
    }