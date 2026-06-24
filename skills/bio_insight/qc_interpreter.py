"""
qc_interpreter.py — QC 结果解读（调用 LLM）

判断 QC 指标是否在正常范围并给出建议。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

QC_INTERPRETER_SYSTEM_PROMPT = """你是一个空间转录组 QC 解读专家。根据用户的 QC 分析结果指标，
判断数据质量并给出建议。

规则：
1. 只基于提供的实际指标做判断
2. 不编造数据中没有的指标
3. 给出可操作的建议
4. 常见正常范围参考：
   - n_obs: 空间转录组通常几千到几万个 spots
   - 过滤比例 <30% 通常可接受
   - 平均 counts 因平台而异
5. 开头标注: "AI 生成，仅供参考" """


def interpret_qc(state: AgentState) -> str:
    """
    解读 QC 结果。

    Args:
        state: AgentState

    Returns:
        QC 解读文字
    """
    step_results = state.get("step_results", {})
    qc_result = step_results.get("qc", {})

    if not qc_result:
        return "AI生成，仅供参考。未找到 QC 分析结果。"

    metrics = qc_result.get("metrics", {})
    summary = qc_result.get("summary", "")

    prompt = (
        f"QC 摘要: {summary}\n"
        f"QC 指标: {metrics}\n\n"
        "请解读这些 QC 结果，判断数据质量是否合格，并给出建议。"
    )

    try:
        interpretation = call_llm(prompt, system=QC_INTERPRETER_SYSTEM_PROMPT, max_tokens=800)
        return interpretation
    except Exception as e:
        return f"AI生成，仅供参考。QC 解读失败: {e}"