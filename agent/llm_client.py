"""
统一的 LLM 调用封装（Anthropic SDK → PPIO 中转）

所有 LLM 调用必须通过此模块，禁止在其他文件直接实例化 Anthropic client。

提供三个接口：
    get_llm_client() -> anthropic.Anthropic
    call_llm(prompt, system, max_tokens) -> str
    call_llm_with_thinking(prompt, system) -> tuple[str, str]
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# 全局单例
_client: Anthropic | None = None


def get_llm_client() -> Anthropic:
    """获取 LLM 客户端单例"""
    global _client
    if _client is None:
        load_dotenv()

        # 同时支持 .env 和 Streamlit Cloud secrets
        api_key = os.getenv("PPIO_API_KEY")
        base_url = os.getenv("PPIO_BASE_URL", "https://api.ppio.com/anthropic")

        # 从 Streamlit secrets 回退（云端部署）
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("PPIO_API_KEY", "")
                base_url = st.secrets.get("PPIO_BASE_URL", base_url)
            except Exception:
                pass

        if not api_key:
            raise ValueError(
                "PPIO_API_KEY not set. Create a .env file with PPIO_API_KEY=your_key, "
                "or set it in Streamlit Cloud Dashboard → Settings → Secrets."
            )
        _client = Anthropic(api_key=api_key, base_url=base_url)
    return _client


def get_model_name() -> str:
    """获取模型名称"""
    return os.getenv("LLM_MODEL_NAME", "deepseek/deepseek-v4-flash")


def call_llm(
    prompt: str,
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """
    调用 LLM，返回文本回复。

    Args:
        prompt: 用户消息内容
        system: 系统提示词（可选）
        max_tokens: 最大输出 token 数

    Returns:
        模型回复的纯文本
    """
    client = get_llm_client()
    model = get_model_name()

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    # 拼接所有文本块（可能包含 ThinkingBlock）
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)
    return "".join(text_parts)


def call_llm_with_thinking(
    prompt: str,
    system: str = "",
) -> tuple[str, str]:
    """
    调用 LLM 并返回 (thinking_content, response_text)。

    Args:
        prompt: 用户消息内容
        system: 系统提示词（可选）

    Returns:
        (thinking_content, response_text) 二元组
    """
    client = get_llm_client()
    model = get_model_name()

    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    thinking = ""
    text = ""
    for block in response.content:
        if hasattr(block, "thinking"):
            thinking = block.thinking
        if hasattr(block, "text"):
            text = block.text

    return thinking, text