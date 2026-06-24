"""
explainer 节点 — 为每步结果生成简短解释（调用 LLM）

职责：
1. 对当前步骤的执行结果（summary + metrics）生成自然语言解释
2. 只描述事实，不编造生物学结论
3. 解释存入 state.explanations[current_step]
"""

from agent.state import AgentState
from agent.llm_client import call_llm

EXPLAINER_SYSTEM_PROMPT = """你是一个空间转录组数据分析助手。请为用户解释某一步分析的结果。

规则：
1. 只说事实——只描述数据中确实存在的指标和结果
2. 不编造具体的基因名、细胞类型或生物学结论
3. 使用通俗易懂的语言
4. 每段解释不超过 5 句话
5. 中英文均可，优先使用用户输入的语言

如果数据中没有提供具体数值，不要编造。只说 "分析已完成" 即可。"""


def explainer_node(state: AgentState) -> dict:
    """为当前步骤生成解释文字"""
    current_step = state.get("current_step", "")
    step_results = state.get("step_results", {})

    if not current_step or current_step not in step_results:
        return {}

    result = step_results[current_step]
    summary = result.get("summary", "")
    metrics = result.get("metrics", {})
    figure_count = len(result.get("figure_paths", []))

    prompt = f"""步骤: {current_step}
结果摘要: {summary}
关键指标: {metrics}
生成图表数: {figure_count}

请用自然语言解释这步分析的结果。"""

    try:
        explanation = call_llm(prompt, system=EXPLAINER_SYSTEM_PROMPT, max_tokens=500)
    except Exception:
        explanation = f"步骤 '{current_step}' 已完成。"

    explanations = dict(state.get("explanations", {}))
    explanations[current_step] = explanation

    return {"explanations": explanations}