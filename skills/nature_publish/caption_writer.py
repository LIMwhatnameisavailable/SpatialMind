"""
caption_writer.py — 图注生成（调用 LLM）

根据图表内容生成符合期刊投稿规范的英文图注。
Prompt 模板从 PROMPTS.md 加载（集成 nature-figure 图注规范）。
"""

from agent.state import AgentState
from agent.llm_client import call_llm
from agent.prompts_loader import load_system_prompt

CAPTION_SYSTEM_PROMPT = load_system_prompt("Caption Writer")


def write_captions(state: AgentState) -> str:
    """
    为分析图表生成图注。

    Args:
        state: AgentState

    Returns:
        图注文本
    """
    completed_steps = state.get("completed_steps", [])
    step_results = state.get("step_results", {})

    if not completed_steps or not step_results:
        return "No analysis results available for figure captions."

    # 构建各步骤的描述信息
    step_descriptions = []
    for step in ["qc", "preprocess", "dimred", "cluster", "spatial", "marker"]:
        if step in step_results:
            result = step_results[step]
            metrics = result.get("metrics", {})
            desc = f"- {step}: {result.get('summary', '')}"
            if metrics:
                desc += f" | 指标: {metrics}"
            step_descriptions.append(desc)

    prompt = (
        "请为以下空间转录组分析结果生成英文图注。分析步骤包括：\n\n"
        + "\n".join(step_descriptions)
        + "\n\n请为每张图生成独立的图注，用 'Figure Xa:', 'Figure Xb:' 等区分。"
    )

    try:
        captions = call_llm(prompt, system=CAPTION_SYSTEM_PROMPT, max_tokens=1500)
        return captions
    except Exception as e:
        return f"图注生成失败: {e}"