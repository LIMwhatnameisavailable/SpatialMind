"""
methods_writer.py — Methods 段落生成（调用 LLM）

根据实际运行的分析参数生成 Methods 段落，符合期刊规范。
Prompt 模板从 PROMPTS.md 加载（集成 nature-writing Methods 规范）。
"""

from agent.state import AgentState
from agent.llm_client import call_llm
from agent.prompts_loader import load_system_prompt

METHODS_SYSTEM_PROMPT = load_system_prompt("Methods Writer")


def write_methods(state: AgentState) -> str:
    """
    根据实际分析参数生成 Methods 段落。

    Args:
        state: AgentState

    Returns:
        Methods 段落文本
    """
    step_results = state.get("step_results", {})
    step_params = state.get("step_params", {})
    data_type = state.get("data_type", "unknown")

    if not step_results:
        return "No analysis methods available to describe."

    # 收集分析细节
    methods_summary = []
    for step, result in step_results.items():
        metrics = result.get("metrics", {})
        params = step_params.get(step, {})
        summary = result.get("summary", "")
        methods_summary.append(f"{step}: {summary}")
        if params:
            methods_summary.append(f"  参数: {params}")
        if metrics:
            methods_summary.append(f"  指标: {metrics}")

    prompt = (
        f"数据类型: {data_type}\n\n"
        f"分析方法与参数:\n"
        + "\n".join(methods_summary)
        + "\n\n请根据以上实际使用的方法，生成一段符合 Nature 期刊规范的 Methods 段落。"
    )

    try:
        methods = call_llm(prompt, system=METHODS_SYSTEM_PROMPT, max_tokens=2000)
        return methods
    except Exception as e:
        return f"Methods 生成失败: {e}"