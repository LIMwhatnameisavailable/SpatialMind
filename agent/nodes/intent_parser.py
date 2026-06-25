"""
intent_parser 节点 — 解析用户自然语言输入

职责：
1. 判断意图类型：qa（问答）/ analysis（分析）
2. qa 意图直接调用 LLM 回答，设置 is_complete=True，跳过分析流程
3. analysis 意图：提取数据路径、数据类型、分析关键词
"""

import os
import re
from agent.state import AgentState
from agent.llm_client import call_llm_with_thinking
import logging

logger = logging.getLogger(__name__)

# qa 意图关键词（命中任意一个 → 纯问答，不启动分析流程）
QA_KEYWORDS = [
    "什么是", "是什么", "介绍", "解释", "为什么", "原理", "概念",
    "怎么理解", "有什么区别", "什么意思", "定义", "背景",
    "what is", "what are", "explain", "why", "how does", "difference between",
    "introduction", "overview", "describe",
]

QA_SYSTEM_PROMPT = """你是空间转录组学领域的专业助手。
用简洁清晰的中文回答用户的问题，适当使用分点说明。
不要编造数据或引用不存在的文献。"""


def _is_qa_intent(user_input: str) -> bool:
    """判断是否为纯问答意图"""
    text = user_input.lower().strip()
    return any(kw in text for kw in QA_KEYWORDS)


def intent_parser_node(state: AgentState) -> dict:
    user_input = state.get("user_input", "")
    session_id = state.get("session_id", "default")
    data_path = state.get("data_path", "")

    # ── QA 意图：直接回答，不进入分析流程 ──────────────────────────
    if _is_qa_intent(user_input):
        logger.info(f"[intent_parser] 识别为 QA 意图: {user_input[:50]}")
        try:
            thinking, answer = call_llm_with_thinking(
                prompt=user_input,
                system=QA_SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.error(f"QA LLM 调用失败: {e}")
            answer = "抱歉，暂时无法回答该问题，请稍后重试。"
            thinking = ""

        return {
            "request_type": "qa",
            "data_path": data_path,
            "data_type": "unknown",
            "adata_cache_key": f"session_{session_id}",
            "analysis_plan": [],
            "current_step": "",
            "completed_steps": [],
            "figures": {},
            "step_results": {"intent_thinking": thinking},
            "explanations": {},
            "skill_outputs": {},
            "error_message": None,
            "retry_count": 0,
            "max_retries": 2,
            "is_complete": True,
            "messages": [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer},
            ],
        }

    # ── Analysis 意图：走正常分析流程 ──────────────────────────────
    logger.info(f"[intent_parser] 识别为 Analysis 意图: {user_input[:50]}")

    # 1. 从输入中提取 .h5ad 路径
    path_patterns = re.findall(r"[\w/\\:.-]+\.h5ad", user_input)
    if path_patterns:
        data_path = os.path.abspath(path_patterns[0])
    elif not data_path:
        for root, dirs, files in os.walk("data"):
            for f in files:
                if f.endswith(".h5ad"):
                    data_path = os.path.abspath(os.path.join(root, f))
                    break
            if data_path:
                break

    # 2. 如果没有可用 .h5ad 数据，禁止进入分析流程，避免 executor 报错
    if not data_path:
        msg = (
            "我还没有检测到可用的空间转录组数据文件。\n\n"
            "请先在侧边栏上传 `.h5ad` 文件，或者在输入中提供 `.h5ad` 文件路径。\n"
            "上传数据后，你可以输入：`执行完整分析`、`只做QC和聚类`、`找空间可变基因`。"
        )

        return {
            "request_type": "no_data",
            "data_path": "",
            "data_type": "unknown",
            "adata_cache_key": f"session_{session_id}",
            "analysis_plan": [],
            "current_step": "",
            "completed_steps": [],
            "figures": {},
            "step_results": {},
            "explanations": {},
            "skill_outputs": {},
            "error_message": None,
            "retry_count": 0,
            "max_retries": 2,
            "is_complete": True,
            "messages": [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": msg},
            ],
        }

    # 3. 数据类型判断
    data_type = "unknown"
    if data_path:
        lower_path = data_path.lower()
        if "stereo" in lower_path:
            data_type = "stereo"
        elif "visium" in lower_path:
            data_type = "visium"

    # 3. 提取分析意图关键词
    intent_keywords = []
    intent_map = {
        "qc": ["qc", "quality", "quality control", "过滤", "质控"],
        "preprocess": ["normalize", "normalization", "归一化", "log", "hvg", "scale"],
        "dimred": ["pca", "umap", "降维", "dimensionality reduction"],
        "cluster": ["cluster", "clustering", "聚类", "leiden", "louvain"],
        "spatial": ["spatial", "空间", "分布", "distribute"],
        "marker": ["marker", "差异基因", "deg", "差异表达"],
        "svg": ["svg", "spatial variable", "空间可变"],
    }
    for step_name, keywords in intent_map.items():
        if any(kw in user_input.lower() for kw in keywords):
            intent_keywords.append(step_name)

    if intent_keywords:
        analysis_plan = ["data_load"] + intent_keywords
    else:
        analysis_plan = ["data_load", "qc", "preprocess", "dimred", "cluster", "spatial", "marker"]

    return {
        "request_type": "analysis",
        "data_path": data_path,
        "data_type": data_type,
        "adata_cache_key": f"session_{session_id}",
        "analysis_plan": analysis_plan,
        "current_step": "",
        "completed_steps": [],
        "figures": {},
        "step_results": {},
        "explanations": {},
        "skill_outputs": {},
        "error_message": None,
        "retry_count": 0,
        "max_retries": 2,
        "is_complete": False,
        "messages": [{"role": "user", "content": user_input}],
    }
