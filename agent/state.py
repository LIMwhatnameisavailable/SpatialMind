"""
AgentState TypedDict 定义

所有字段说明见 CLAUDE.md。严禁修改已有字段名（只能新增）。
AnnData 对象通过 ADATA_CACHE 全局缓存访问，不存入 State。
"""

import uuid
from typing import Any, Optional, TypedDict


class AgentState(TypedDict):
    # ── 用户输入 ──
    user_input: str               # 原始自然语言输入
    session_id: str               # 会话 ID，用于 SqliteSaver
    request_type: str             # "qa" | "analysis" | "no_data" | "result_explanation" | "unknown"

    # ── 数据状态 ──
    data_path: str                # h5ad 文件路径
    data_type: str                # "stereo" | "visium" | "unknown"
    adata_cache_key: str          # adata 在内存缓存中的 key

    # ── 分析计划 ──
    analysis_plan: list[str]      # 规划的步骤列表
    current_step: str             # 当前执行的步骤名
    completed_steps: list[str]    # 已完成的步骤
    step_params: dict[str, Any]   # 每步骤的参数

    # ── 结果存储 ──
    figures: dict[str, str]       # 步骤名 -> 图片文件路径
    step_results: dict[str, Any]  # 步骤名 -> 结果摘要
    explanations: dict[str, str]  # 步骤名 -> LLM 生成的解释文字

    # ── Skills 输出 ──
    skill_outputs: dict[str, Any] # skill 名 -> 输出内容

    # ── 错误与控制 ──
    error_message: str | None     # 当前错误信息
    retry_count: int              # 当前步骤重试次数
    max_retries: int              # 最大重试次数（默认 2）
    is_complete: bool             # 整体流程是否完成

    # ── LLM 对话历史 ──
    messages: list[dict]          # 多轮对话消息历史


def get_initial_state(
    user_input: str = "",
    data_path: str = "",
    data_type: str = "unknown",
    step_params: Optional[dict[str, Any]] = None,
    session_id: Optional[str] = None,
    output_dir: str = "outputs/figures",
) -> AgentState:
    """
    创建 AgentState 的初始化实例。

    封装所有默认字段，避免在调用处重复编写初始化字典。
    用于 app.py 和 test 文件。

    Args:
        user_input: 用户自然语言输入
        data_path: h5ad 文件路径
        data_type: "stereo" | "visium" | "unknown"
        step_params: 可选的分析参数覆盖
        session_id: 可选，不传则自动生成 UUID

    Returns:
        填充好默认值的 AgentState TypedDict
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    return {
        "user_input": user_input,
        "session_id": session_id,
        "request_type": "unknown",
        "output_dir": output_dir,
        "data_path": data_path,
        "data_type": data_type,
        "adata_cache_key": session_id,
        "analysis_plan": [],
        "current_step": "",
        "completed_steps": [],
        "step_params": step_params or {},
        "figures": {},
        "step_results": {},
        "explanations": {},
        "skill_outputs": {},
        "error_message": None,
        "retry_count": 0,
        "max_retries": 2,
        "is_complete": False,
        "messages": [],
    }
