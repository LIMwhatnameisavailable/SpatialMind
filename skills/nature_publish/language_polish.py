"""
language_polish.py — 语言润色（调用 LLM）

将分析摘要润色为学术英文，提升语言质量。
Prompt 模板从 PROMPTS.md 加载（集成 nature-polishing 句式规范）。
"""

from agent.state import AgentState
from agent.llm_client import call_llm
from agent.prompts_loader import load_system_prompt

POLISH_SYSTEM_PROMPT = load_system_prompt("Language Polish")


def polish_text(text: str) -> str:
    """
    润色单段文本。

    Args:
        text: 原始文本

    Returns:
        润色后的学术英文
    """
    if not text.strip():
        return text

    try:
        polished = call_llm(text, system=POLISH_SYSTEM_PROMPT, max_tokens=2000)
        return polished
    except Exception as e:
        return f"润色失败: {e}"


def polish_all(state: AgentState) -> dict:
    """
    润色所有解释文字。

    Args:
        state: AgentState

    Returns:
        {"polished_explanations": dict}
    """
    explanations = state.get("explanations", {})
    polished = {}
    for step, text in explanations.items():
        polished[step] = polish_text(text)

    return {"polished_explanations": polished}