"""
next_step.py — 建议下一步分析（调用 LLM）

基于当前分析状态推荐后续分析方向。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

NEXT_STEP_SYSTEM_PROMPT = """你是一个空间转录组分析顾问。根据用户已完成的分析步骤和结果，
推荐下一步最有价值的分析方向。

可推荐的后续分析方向包括：
1. 空间可变基因（SVG）分析
2. 细胞通讯分析（CellChat / Squidpy）
3. GO/KEGG 富集分析
4. 差异表达分析（不同条件间）
5. 轨迹推断
6. 多切片整合分析

请根据已有结果推荐最相关的 1-3 个方向，并说明理由。
开头标注: "AI 生成，仅供参考" """


def suggest_next_steps(state: AgentState) -> str:
    """
    建议下一步分析方向。

    Args:
        state: AgentState

    Returns:
        建议文字
    """
    completed_steps = state.get("completed_steps", [])
    step_results = state.get("step_results", {})

    if not completed_steps:
        return "AI生成，仅供参考。尚未完成任何分析步骤，建议从数据加载和 QC 开始。"

    summaries = []
    for step in completed_steps:
        if step in step_results:
            summaries.append(f"{step}: {step_results[step].get('summary', '')}")

    prompt = (
        "已完成的分析步骤:\n"
        + "\n".join(summaries)
        + "\n\n请推荐下一步最有价值的分析方向。"
    )

    try:
        suggestions = call_llm(prompt, system=NEXT_STEP_SYSTEM_PROMPT, max_tokens=800)
        return suggestions
    except Exception as e:
        return f"AI生成，仅供参考。建议生成失败: {e}"