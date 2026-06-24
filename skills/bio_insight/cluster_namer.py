"""
cluster_namer.py — Cluster 命名（LLM + CellMarker API）

根据 marker genes 自动为 cluster 命名。
需引用 step_results 中的真实数据，不编造生物学结论。
"""

from agent.state import AgentState
from agent.llm_client import call_llm

CLUSTER_NAMER_SYSTEM_PROMPT = """你是一个细胞类型注释专家。根据用户提供的 cluster 及其 marker genes，
结合已知的细胞类型标记基因知识，为每个 cluster 推断最可能的细胞类型名称。

规则：
1. 必须只使用用户提供的 gene list 中的基因作为依据
2. 输出格式: "Cluster 0: Cell Type A\nCluster 1: Cell Type B"
3. 如果不确定，标注 "Unknown/Unclear"
4. 对每个命名给出简短依据（2-3 个基因名）
5. 输出开头标注: "AI 生成，仅供参考" """


def name_clusters(state: AgentState) -> dict:
    """
    根据 marker gene 分析结果为 cluster 命名。

    Args:
        state: AgentState

    Returns:
        {"cluster_names": dict, "disclaimer": str}
        如: {"cluster_names": {"0": "T cell", "1": "B cell"}, "disclaimer": "..."}
    """
    step_results = state.get("step_results", {})
    marker_result = step_results.get("marker", {})

    if not marker_result or "metrics" not in marker_result:
        return {
            "cluster_names": {},
            "disclaimer": "AI生成内容，仅供参考。未找到 marker gene 分析结果。",
        }

    metrics = marker_result.get("metrics", {})
    n_clusters = metrics.get("n_clusters", 0)

    # 获取实际 marker genes (从 adata 缓存)
    from tools import ADATA_CACHE
    adata_key = state.get("adata_cache_key", "")
    marker_genes = {}

    if adata_key in ADATA_CACHE:
        adata = ADATA_CACHE[adata_key]
        if "rank_genes_groups" in adata.uns:
            names = adata.uns["rank_genes_groups"]["names"]
            for cluster_id in range(min(len(names), n_clusters)):
                genes = [names[cluster_id][i] for i in range(min(5, len(names[cluster_id])))]
                marker_genes[str(cluster_id)] = genes

    if not marker_genes:
        return {
            "cluster_names": {},
            "disclaimer": "AI生成内容，仅供参考。未找到 marker genes 数据。",
        }

    prompt = "请为以下 cluster 及其 marker genes 推断细胞类型：\n\n"
    for cluster_id, genes in marker_genes.items():
        prompt += f"Cluster {cluster_id}: {', '.join(genes)}\n"
    prompt += "\n请返回细胞类型名称及简短依据。"

    try:
        response = call_llm(prompt, system=CLUSTER_NAMER_SYSTEM_PROMPT, max_tokens=1000)
    except Exception as e:
        response = f"AI 生成失败: {e}"

    return {
        "cluster_names_raw": response,
        "disclaimer": "AI 生成内容，仅供参考，不构成科学结论。",
    }