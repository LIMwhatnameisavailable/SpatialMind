"""
planner 节点 — 生成分析计划（调用 LLM，启用 ThinkingBlock）

职责：
1. 接收 intent_parser 解析后的用户意图和数据信息
2. 调用 LLM（带 Thinking）生成有序的分析步骤列表
3. 根据用户输入参数偏好设置 step_params
4. 写入 analysis_plan 和 step_params
"""

from agent.state import AgentState
from agent.llm_client import call_llm_with_thinking

PLANNER_SYSTEM_PROMPT = """你是一个空间转录组数据分析的规划专家。你的任务是根据用户的需求和数据信息，生成一个有序的分析步骤计划。

可用的分析步骤（按推荐执行顺序排列）：
1. data_load — 数据加载：读取 .h5ad 文件并缓存到内存
2. qc — 质量控制：过滤低质量细胞/基因，线粒体基因过滤，生成QC图
3. preprocess — 预处理：归一化、log转换、HVG筛选、标准化
4. dimred — 降维：PCA + UMAP
5. cluster — 聚类：Leiden/Louvain 聚类
6. spatial — 空间可视化：细胞空间分布、基因空间表达
7. marker — Marker Gene 分析：差异表达分析、点图、热图
8. svg — 空间可变基因分析（可选扩展）

输出格式要求：
- 第一行及以上是你的思考过程（中英文均可）
- 最后三行必须是：
  PLAN_STEPS: step1, step2, step3, ...
  PARAMS: {"step_name": {"param": "value"}, ...}
  THINKING_END

如果没有特殊参数需求，PARAMS 可以为空字典 {}。

注意：
- 不要编造不存在的步骤名
- 如果用户只要求部分分析，只输出用户需要的步骤
- 步骤顺序要符合数据分析逻辑（前一步的输出是后一步的输入）
"""


def planner_node(state: AgentState) -> dict:
    """生成分析计划和参数配置"""
    user_input = state.get("user_input", "")
    data_path = state.get("data_path", "")
    data_type = state.get("data_type", "unknown")
    intent_plan = state.get("analysis_plan", [])

    # 构造 prompt
    prompt = f"""用户输入: {user_input}
数据路径: {data_path}
数据类型: {data_type}
初步意图分析结果: {', '.join(intent_plan) if intent_plan else '未检测到明确意图'}

请根据以上信息，生成最终的分析计划。如果用户没有指定具体步骤，默认执行全流程。"""

    thinking, response_text = call_llm_with_thinking(
        prompt=prompt,
        system=PLANNER_SYSTEM_PROMPT,
    )

    # 解析响应
    plan_steps = list(intent_plan)  # 默认使用 intent_parser 的意图
    step_params: dict = {}

    # 尝试从响应中解析 PLAN_STEPS 行
    for line in response_text.strip().split("\n"):
        line = line.strip()
        if line.startswith("PLAN_STEPS:"):
            steps_str = line[len("PLAN_STEPS:"):].strip()
            if steps_str:
                plan_steps = [s.strip() for s in steps_str.split(",") if s.strip()]
        elif line.startswith("PARAMS:"):
            params_str = line[len("PARAMS:"):].strip()
            if params_str and params_str != "{}":
                try:
                    import json
                    step_params = json.loads(params_str)
                except json.JSONDecodeError:
                    step_params = {}

    return {
        "analysis_plan": plan_steps,
        "step_params": step_params,
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": f"[Planner 思考过程]\n{thinking}\n\n[分析计划]\n{', '.join(plan_steps)}"}
        ],
    }