"""
planner 节点 — 真正动态的LLM分析规划（重写版）
"""

from agent.state import AgentState
from agent.llm_client import call_llm_with_thinking
import json
import logging

logger = logging.getLogger(__name__)

AVAILABLE_STEPS = ["data_load", "qc", "preprocess", "dimred", "cluster", "spatial", "marker", "svg"]

FULL_DEFAULT_PLAN = ["data_load", "qc", "preprocess", "dimred", "cluster", "spatial", "marker"]

PLANNER_SYSTEM_PROMPT = """你是空间转录组数据分析规划专家。根据用户的自然语言需求，制定精确的分析计划。

可用步骤（必须从这8个中选择，不可创造新步骤名）：
- data_load: 读取.h5ad文件（几乎总是需要，除非数据已加载）
- qc: 质量控制，细胞/基因过滤，线粒体基因过滤
- preprocess: 归一化、log转换、HVG筛选、标准化
- dimred: PCA降维 + UMAP可视化
- cluster: Leiden聚类
- spatial: 空间分布可视化（需要空间坐标）
- marker: Marker gene差异表达分析
- svg: 空间可变基因分析（计算密集，仅用户明确要求时添加）

参数调整规则：
- 用户说"严格QC"/"高质量" → qc: {"min_genes": 500, "min_cells": 10, "max_pct_mt": 10}
- 用户说"宽松QC"/"保留更多细胞" → qc: {"min_genes": 100, "min_cells": 3, "max_pct_mt": 30}
- 用户说"高分辨率聚类"/"更多cluster" → cluster: {"resolution": 1.2}
- 用户说"低分辨率"/"少量cluster" → cluster: {"resolution": 0.3}
- 用户说"只看某个基因" → spatial: {"gene_name": "基因名"}
- 用户说"快速分析"/"只看基础" → 跳过svg: qc, preprocess, dimred, cluster, spatial; 可跳过marker
- 用户说"完整分析"/"全流程" → 不含svg；svg是计算密集型功能，仅用户明确要求时添加

输出格式（严格遵守，最后两行必须是这个格式）：
PLAN_STEPS: step1, step2, step3
PARAMS: {"step_name": {"param": "value"}}

示例输出：
用户只想看聚类和空间分布 →
PLAN_STEPS: data_load, qc, preprocess, dimred, cluster, spatial
PARAMS: {}

用户想做完整分析且高分辨率聚类 →
PLAN_STEPS: data_load, qc, preprocess, dimred, cluster, spatial, marker
PARAMS: {"cluster": {"resolution": 1.0}}
"""


def planner_node(state: AgentState) -> dict:
    user_input = state.get("user_input", "")
    data_path = state.get("data_path", "")
    data_type = state.get("data_type", "unknown")
    completed_steps = state.get("completed_steps", [])

    # 构造 prompt：只给用户原始输入，不给 intent_parser 的结果
    already_done = f"\n已完成步骤（无需重复）: {completed_steps}" if completed_steps else ""

    prompt = f"""用户需求: {user_input}
数据路径: {data_path}
数据类型: {data_type}{already_done}

请根据用户需求制定分析计划。"""

    try:
        thinking, response_text = call_llm_with_thinking(
            prompt=prompt,
            system=PLANNER_SYSTEM_PROMPT,
        )
    except Exception as e:
        logger.error(f"Planner LLM调用失败: {e}")
        thinking = ""
        response_text = f"PLAN_STEPS: {', '.join(FULL_DEFAULT_PLAN)}\nPARAMS: {{}}"

    # 解析 LLM 输出
    plan_steps = None
    step_params = {}

    for line in response_text.strip().split("\n"):
        line = line.strip()
        if line.startswith("PLAN_STEPS:"):
            steps_str = line[len("PLAN_STEPS:"):].strip()
            parsed = [s.strip() for s in steps_str.split(",") if s.strip()]
            # 验证：只保留合法步骤名
            valid = [s for s in parsed if s in AVAILABLE_STEPS]
            if valid:
                plan_steps = valid
        elif line.startswith("PARAMS:"):
            params_str = line[len("PARAMS:"):].strip()
            if params_str and params_str != "{}":
                try:
                    step_params = json.loads(params_str)
                except json.JSONDecodeError:
                    step_params = {}

    # 只有在LLM完全失败时才降级
    if plan_steps is None:
        logger.warning("Planner LLM未返回有效计划，使用默认全流程")
        plan_steps = FULL_DEFAULT_PLAN

    # 确保 data_load 始终是第一步
    if "data_load" not in plan_steps:
        plan_steps = ["data_load"] + plan_steps

    return {
        "analysis_plan": plan_steps,
        "step_params": step_params,
        "step_results": {
            **state.get("step_results", {}),
            "planner_thinking": thinking,
        },
        "messages": state.get("messages", []) + [
            {
                "role": "assistant",
                "content": f"📋 分析计划已生成：{' → '.join(plan_steps)}\n参数：{step_params if step_params else '默认参数'}"
            }
        ],
    }