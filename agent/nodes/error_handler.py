"""
error_handler 节点 — 错误捕获与重试决策（不调用 LLM）

职责：
1. 记录错误信息到 state
2. 根据 retry_count 和 max_retries 决定：
   - retry_count < max_retries: 返回 executor 重试（可以调整参数）
   - retry_count >= max_retries: 返回 planner 重新规划（跳过此步骤）
"""

from agent.state import AgentState


def error_handler_node(state: AgentState) -> dict:
    """处理执行错误，决定下一步操作"""
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    current_step = state.get("current_step", "")
    error_message = state.get("error_message", "未知错误")

    # 记录日志（通过 messages）
    error_entry = {
        "role": "system",
        "content": f"[ErrorHandler] 步骤 '{current_step}' 失败 (第 {retry_count} 次): {error_message}",
    }

    if retry_count < max_retries:
        # 可以重试——可能有不同参数
        # 将失败的步骤从 completed_steps 中移除以便重新执行
        completed = list(state.get("completed_steps", []))
        if current_step in completed:
            completed.remove(current_step)

        return {
            "completed_steps": completed,
            "retry_count": retry_count + 1,  # 递增重试计数
            "messages": state.get("messages", []) + [error_entry],
            # executor 会根据 retry_count 和 error_message 决定是否调整参数
        }
    else:
        # 超过最大重试次数 —— 跳过此步骤
        # 将当前步骤标记为已跳过
        skipped_entry = {
            "role": "system",
            "content": f"[ErrorHandler] 步骤 '{current_step}' 重试 {max_retries} 次仍失败，跳过此步骤。",
        }

        # 检查是否所有步骤都已完成（包括跳过的）
        completed = list(state.get("completed_steps", []))
        plan = state.get("analysis_plan", [])
        all_done_or_skipped = all(s in completed for s in plan)

        return {
            "step_results": {
                **state.get("step_results", {}),
                current_step: {
                    "summary": f"步骤被跳过（{max_retries} 次重试后仍失败）",
                    "metrics": {"skipped": True, "error": error_message},
                    "figure_paths": [],
                },
            },
            "messages": state.get("messages", []) + [error_entry, skipped_entry],
            "is_complete": all_done_or_skipped,
            "error_message": None,
            "retry_count": 0,
        }