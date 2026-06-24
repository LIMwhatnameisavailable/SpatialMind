"""
intent_parser 节点 — 解析用户自然语言输入

职责：
1. 提取数据路径（如果用户在输入中指定了文件路径）
2. 判断数据类型（stereo / visium）
3. 提取分析意图和参数偏好
4. 填充 AgentState 的初始字段

不调用 LLM，使用规则匹配 + Scanpy 读取摘要判断数据类型。
"""

import os
import re
from agent.state import AgentState


def intent_parser_node(state: AgentState) -> dict:
    """
    解析用户输入，返回对 AgentState 的更新。
    """
    user_input = state.get("user_input", "")
    session_id = state.get("session_id", "default")
    data_path = state.get("data_path", "")

    # 1. 尝试从输入中提取 .h5ad 文件路径
    path_patterns = re.findall(r"[\w/\\:.-]+\.h5ad", user_input)
    if path_patterns:
        data_path = os.path.abspath(path_patterns[0])
    elif not data_path:
        # 尝试在 data/ 下自动查找
        for root, dirs, files in os.walk("data"):
            for f in files:
                if f.endswith(".h5ad"):
                    data_path = os.path.abspath(os.path.join(root, f))
                    break
            if data_path:
                break

    # 2. 根据路径关键词判断数据类型
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

    # 4. 生成初始 analysis_plan（始终以 data_load 为首步确保数据已加载）
    if intent_keywords:
        analysis_plan = ["data_load"] + intent_keywords
    else:
        # 默认全流程
        analysis_plan = ["data_load", "qc", "preprocess", "dimred", "cluster", "spatial", "marker"]

    # 5. 确保每个路径唯一
    adata_cache_key = f"session_{session_id}"

    return {
        "data_path": data_path,
        "data_type": data_type,
        "adata_cache_key": adata_cache_key,
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