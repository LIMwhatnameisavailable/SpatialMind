"""
prompts_loader.py — 从 PROMPTS.md 加载 prompt 模板

将技能级别的 prompt 统一存放在 PROMPTS.md 中，通过此模块加载，
避免在 skills 代码中硬编码长 prompt 字符串。

用法:
    from agent.prompts_loader import load_system_prompt

    # 在 PROMPTS.md 中找标题包含 "Caption Writer" 的 section，
    # 提取其中的第一个代码块内容作为 System Prompt
    CAPTION_SYSTEM_PROMPT = load_system_prompt("Caption Writer")
"""

import re
from pathlib import Path

_PROMPTS_PATH = Path(__file__).resolve().parent.parent / "PROMPTS.md"


def _read_prompts_file() -> str:
    """读取 PROMPTS.md 文件内容"""
    if not _PROMPTS_PATH.exists():
        raise FileNotFoundError(f"PROMPTS.md 不存在: {_PROMPTS_PATH}")
    return _PROMPTS_PATH.read_text(encoding="utf-8")


def _find_section_boundaries(text: str, title_keyword: str) -> tuple[int, int] | None:
    """
    在 text 中查找标题包含 title_keyword 的 section，返回 (start, end)。

    匹配规则：行首以 `## ` 或 `### ` 开头，且该行文本中包含 title_keyword。
    终止规则：找到下一个与起始同级别或更高级别的标题行（即如果起始是 `## `，
    则只认下一个 `## ` 或更高级别为终止；`### ` 则认 `### `、`## ` 或 `# `）。
    """
    lines = text.split("\n")
    section_start = None
    start_level = None  # 2 for "##", 3 for "###"

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            if title_keyword in stripped and section_start is None:
                section_start = i
                start_level = 2 if stripped.startswith("## ") else 3
                break

    if section_start is None:
        return None

    # 找到下一个同级或更高级别的标题
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("# "):
            section_end = i
            break
        if stripped.startswith("## ") and start_level >= 2:
            section_end = i
            break
        if stripped.startswith("### ") and start_level >= 3:
            section_end = i
            break
        # 忽略 start_level 以下的标题（如 ### 不会终止 ##）

    char_start = sum(len(l) + 1 for l in lines[:section_start])
    char_end = sum(len(l) + 1 for l in lines[:section_end])
    return (char_start, char_end)


def _extract_first_code_block(text: str) -> str | None:
    """
    从 text 中提取第一个 ```text 或 ``` 代码块的内容（不含标记）。
    """
    # 优先匹配 ```text ... ```
    m = re.search(r"```text\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # 回退到 ``` ... ```
    m = re.search(r"```\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def load_system_prompt(title_keyword: str) -> str:
    """
    从 PROMPTS.md 中查找标题包含 title_keyword 的 section，
    提取该 section 下的第一个代码块作为 System Prompt。

    Args:
        title_keyword: PROMPTS.md 中 section 标题的关键词（如 "Language Polish"）

    Returns:
        prompt 模板字符串

    Raises:
        ValueError: 如果找不到对应的 section 或代码块
    """
    content = _read_prompts_file()
    boundaries = _find_section_boundaries(content, title_keyword)
    if boundaries is None:
        raise ValueError(
            f"PROMPTS.md 中未找到标题包含 '{title_keyword}' 的 section。"
            f"可用的 section 标题关键词："
            f" Planner / Checker / Explainer / Caption Writer / Methods Writer"
            f" / Cluster Namer / Insight Extractor / Language Polish"
        )

    start, end = boundaries
    section_text = content[start:end]

    prompt = _extract_first_code_block(section_text)
    if prompt is None:
        raise ValueError(
            f"Section 包含 '{title_keyword}' 的 section 中未找到代码块"
        )
    return prompt
