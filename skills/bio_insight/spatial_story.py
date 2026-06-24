"""
spatial_story.py — 空间叙事文字生成（调用 LLM）

将空间分布数据转化为可读的生物学描述。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

SPATIAL_STORY_SYSTEM_PROMPT = """你是一个空间转录组数据解读专家。请根据用户的聚类和空间分布结果，
生成一段描述性的"空间叙事"文字。

要求：
1. 只描述数据中存在的空间模式和聚类分布
2. 使用通俗但专业的语言
3. 不编造未经数据支持的细胞互作或生物学功能
4. 可以描述"哪些 cluster 在空间上邻近"而非给出功能结论
5. 中英文均可
6. 输出开头标注: "AI 生成内容，仅供参考" """


def generate_spatial_story(state: AgentState) -> str:
    """
    生成空间分布叙事文字。

    Args:
        state: AgentState

    Returns:
        叙事文本
    """
    step_results = state.get("step_results", {})
    spatial_result = step_results.get("spatial", {})
    cluster_result = step_results.get("cluster", {})
    figures = state.get("figures", {})

    # 收集空间和聚类信息
    spatial_summary = spatial_result.get("summary", "")
    cluster_summary = cluster_result.get("summary", "无聚类数据")
    cluster_metrics = cluster_result.get("metrics", {})
    has_spatial_fig = "spatial" in figures

    prompt = (
        f"空间分析结果: {spatial_summary}\n"
        f"聚类结果: {cluster_summary}\n"
        f"聚类指标: {cluster_metrics}\n"
        f"是否生成空间分布图: {has_spatial_fig}\n\n"
        "请根据以上数据生成一段空间叙事文字。"
    )

    try:
        story = call_llm(prompt, system=SPATIAL_STORY_SYSTEM_PROMPT, max_tokens=1000)
        return story
    except Exception as e:
        return f"AI生成内容，仅供参考。空间叙事生成失败: {e}"