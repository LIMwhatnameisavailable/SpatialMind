"""
insight_extractor.py — 提炼关键发现（调用 LLM，带免责声明）

从所有分析结果中提炼关键的生物学发现。
必须标注 AI 生成，不编造数据。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

INSIGHT_SYSTEM_PROMPT = """你是一个空间转录组数据分析报告撰写专家。请根据所有分析步骤的结果，
提炼出 3-5 条关键发现。

规则（必须严格遵守）：
1. 每一条发现都必须有 step_results 中的真实数据支持
2. 不要编造任何具体的基因名、细胞类型或生物学结论
3. 如果数据中没有明确结论，只描述"观察到…模式"而非下结论
4. 每条发现用一句话概括，后跟数据依据
5. 开头和结尾都要标注免责声明
6. 使用专业但谨慎的语言

输出格式：
[免责声明]
1. 发现一（依据：XX指标）
2. 发现二（依据：XX指标）
...
[重复免责声明]"""


def extract_insights(state: AgentState) -> str:
    """
    提炼关键发现。

    Args:
        state: AgentState

    Returns:
        关键发现文本
    """
    step_results = state.get("step_results", {})
    completed_steps = state.get("completed_steps", [])

    if not step_results or not completed_steps:
        return "AI生成内容，仅供参考。无分析数据可供提取关键发现。"

    details = []
    for step in completed_steps:
        if step in step_results:
            result = step_results[step]
            details.append(
                f"步骤 {step}:\n"
                f"  摘要: {result.get('summary', '')}\n"
                f"  指标: {result.get('metrics', {})}"
            )

    prompt = (
        "根据以下空间转录组分析结果，提炼关键发现：\n\n"
        + "\n".join(details)
        + "\n\n请提炼 3-5 条有数据支持的关键发现。"
    )

    try:
        insights = call_llm(prompt, system=INSIGHT_SYSTEM_PROMPT, max_tokens=1000)
        return insights
    except Exception as e:
        return (
            "AI生成内容，仅供参考。\n"
            f"关键发现提取失败: {e}\n"
            "AI生成内容，仅供参考。"
        )