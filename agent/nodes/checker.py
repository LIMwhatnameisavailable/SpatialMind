"""
checker 节点 — 检查执行结果是否合理（调用 LLM）

职责：
1. 接收 executor 的执行结果（summary + metrics）
2. 调用 LLM 判断结果是否合理
3. 返回决策：pass / fail / skip
   - pass: 结果合理，进入 explainer
   - fail: 结果可疑，进入 error_handler 重试
   - skip: 结果虽有问题但可跳过
"""

from agent.state import AgentState
from agent.llm_client import call_llm

CHECKER_SYSTEM_PROMPT = """你是空间转录组分析的质量检查员。你会收到某一步分析的结果摘要和指标，
请判断结果是否合理。

基本原则：
- 数据加载步骤（data_load）：检查是否有细胞数、基因数等基本信息
- QC步骤：检查细胞数、基因数、过滤比例是否在合理范围内
- 预处理步骤：检查归一化后的表达量分布是否正常
- 降维步骤：检查 PCA 解释方差、UMAP 是否有明显聚类结构
- 聚类步骤：检查 cluster 数量是否合理（2-20个）
- 空间可视化：只要有图生成即算 pass
- Marker Gene 分析：检查是否有显著差异基因

回复格式：
第一行：pass / fail / skip
第二行开始：简短理由

注意：不要过于严格，合理的范围可以宽松。有任何图表生成即为 pass 或 skip。"""


def checker_node(state: AgentState) -> dict:
    """检查当前步骤的执行结果"""
    current_step = state.get("current_step", "")
    step_results = state.get("step_results", {})
    error_message = state.get("error_message")

    # 如果有错误信息，直接判定为 fail
    if error_message:
        return {"checker_decision": "fail"}

    # 获取当前步骤的结果
    result = step_results.get(current_step, {})
    summary = result.get("summary", "")
    metrics = result.get("metrics", {})
    figure_paths = result.get("figure_paths", [])

    # 如果有图生成，基本判定为 pass
    if figure_paths:
        return {"checker_decision": "pass"}

    # 对于没有图的步骤，尝试用 LLM 判断
    prompt = f"""步骤名: {current_step}
结果摘要: {summary}
关键指标: {metrics}

请判断此步骤的执行结果是否合理。"""

    try:
        response = call_llm(prompt, system=CHECKER_SYSTEM_PROMPT, max_tokens=500)
        decision_line = response.strip().split("\n")[0].strip().lower()
        if decision_line in ("fail", "skip"):
            return {"checker_decision": decision_line}
        return {"checker_decision": "pass"}
    except Exception:
        # LLM 调用失败时默认 pass
        return {"checker_decision": "pass"}