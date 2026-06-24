"""
cover_letter.py — Cover Letter 生成（调用 LLM）

基于分析结果生成投稿信草稿。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

COVER_LETTER_SYSTEM_PROMPT = """你是一个学术论文 Cover Letter 撰写专家。请根据分析结果和研究背景，
生成一封给期刊编辑的 Cover Letter。

规范格式：
1. 收件人: Dear Editor,
2. 第一段: 介绍研究主题和文章标题（使用占位符）
3. 第二段: 强调研究的主要发现和重要性（基于真实分析结果）
4. 第三段: 说明研究的创新性和对领域的贡献
5. 建议审稿人（可选）
6. 声明无一稿多投、作者同意等
7. 落款

注意：
- 不编造未经数据支持的重大发现
- 语气自信但实事求是
- 长度约 300-500 词"""


def generate_cover_letter(state: AgentState) -> str:
    """
    生成投稿信。

    Args:
        state: AgentState

    Returns:
        Cover letter 文本
    """
    step_results = state.get("step_results", {})
    summaries = []
    for step, result in step_results.items():
        summary = result.get("summary", "")
        if summary:
            summaries.append(f"{step}: {summary}")

    prompt = (
        "基于以下空间转录组分析结果，生成一封投稿信：\n\n"
        + "\n".join(summaries)
        + "\n\n请生成完整的 Cover Letter。"
    )

    try:
        letter = call_llm(prompt, system=COVER_LETTER_SYSTEM_PROMPT, max_tokens=2000)
        return letter
    except Exception as e:
        return f"Cover Letter 生成失败: {e}"