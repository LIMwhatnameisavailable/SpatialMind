"""
lit_reader.py — PDF 文献阅读与总结（pypdf + LLM）

上传 PDF 文献，提取关键发现并与当前分析数据关联。
"""

import os
from agent.state import AgentState
from agent.llm_client import call_llm

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

LIT_READER_SYSTEM_PROMPT = """你是一个科学文献阅读助手。请根据提供的文献内容摘要，
提取关键发现并与当前空间转录组分析相关联。

请按以下格式输出：
1. 文献标题和发表信息（如果有）
2. 研究目的
3. 关键发现（3-5 条）
4. 使用的方法（特别是空间转录组相关方法）
5. 与本分析的相关性

开头标注: "AI 生成内容，仅供参考" """


def read_pdf(file_path: str, state: AgentState) -> str:
    """
    读取 PDF 文献并生成总结。

    Args:
        file_path: PDF 文件路径
        state: AgentState（用于提供分析上下文）

    Returns:
        文献总结
    """
    if not HAS_PYPDF:
        return "AI生成，仅供参考。pypdf 未安装，无法读取 PDF。请安装: pip install pypdf"

    if not os.path.exists(file_path):
        return f"AI生成，仅供参考。文件不存在: {file_path}"

    try:
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages[:20]:  # 最多读 20 页
            text_parts.append(page.extract_text())

        full_text = "\n".join(text_parts)
        # 只取前 3000 字符作为摘要
        summary_text = full_text[:3000]

        # 获取当前分析上下文
        step_results = state.get("step_results", {})
        context = ""
        for step, result in step_results.items():
            context += f"{step}: {result.get('summary', '')}\n"

        prompt = (
            f"文献内容摘要:\n{summary_text}\n\n"
            f"当前分析上下文:\n{context}\n\n"
            "请总结这篇文献的关键发现，并说明与当前分析的相关性。"
        )

        response = call_llm(prompt, system=LIT_READER_SYSTEM_PROMPT, max_tokens=1500)
        return response

    except Exception as e:
        return f"AI生成，仅供参考。文献阅读失败: {e}"