"""
marker_genes.py — Marker Gene 分析

功能：
1. 差异表达分析（sc.tl.rank_genes_groups）
2. 点图（sc.pl.dotplot）
3. 热图（sc.pl.heatmap）
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, save_figure


def run_marker_analysis(adata_key: str, **params) -> dict:
    """
    执行 Marker Gene 分析。

    Args:
        adata_key: 缓存 key
        **params: groupby (cluster key), method, n_genes

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]

    # 找到聚类 key
    groupby = params.get("groupby", None)
    if not groupby:
        for key in ("leiden", "louvain", "clusters"):
            if key in adata.obs:
                groupby = key
                break

    if not groupby:
        return {
            "status": "error",
            "summary": "",
            "figure_paths": [],
            "metrics": {},
            "error": "未找到聚类结果，请先执行聚类分析",
        }

    method = params.get("method", "wilcoxon")
    n_genes = params.get("n_genes", 20)

    try:
        # 差异表达分析
        sc.tl.rank_genes_groups(adata, groupby=groupby, method=method, n_genes=n_genes)
        ADATA_CACHE[adata_key] = adata

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度
        fig_paths = []

        # 提取 marker genes — rank_genes_groups 的 names 是结构化数组
        # dtype 为 [(str(i), 'O') for i in range(n_clusters)]
        n_markers_per_cluster = len(adata.uns["rank_genes_groups"]["names"])
        n_clusters_detected = len(adata.uns["rank_genes_groups"]["names"].dtype)

        # 生成 UMAP 着色图：用前 3 个 cluster 的各 top 1 基因
        top_genes = []
        for c in range(min(3, n_clusters_detected)):
            g = str(adata.uns["rank_genes_groups"]["names"][0][c])
            if g in adata.var_names:
                top_genes.append(g)
        n_plots = len(top_genes)
        if n_plots > 0:
            # 1. 先创建画布
            fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 4))
            # 2. 再应用全局样式
            apply_global_style()
            if n_plots == 1:
                axes = [axes]
            # 3. 绘图时显式传入 ax
            for i, gene in enumerate(top_genes):
                sc.pl.umap(adata, color=gene, ax=axes[i], show=False, title=gene)
            # 4. 手动修复 scanpy 可能覆盖的样式
            for ax in axes:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
            plt.tight_layout()
            # 5. 保存
            fig_path = f"outputs/figures/marker_umap_{timestamp}.png"
            save_figure(fig, "outputs/figures", stem=f"marker_umap_{timestamp}", dpi=150)
            plt.close(fig)
            fig_paths.append(fig_path)

        n_total_clusters = n_clusters_detected

        summary = (
            f"Marker gene 分析完成: 使用 {method} 方法, "
            f"在 {n_total_clusters} 个 cluster 中各找到 top {n_markers_per_cluster} 个 marker genes"
        )

        return {
            "status": "success",
            "summary": summary,
            "figure_paths": fig_paths,
            "metrics": {
                "method": method,
                "groupby": groupby,
                "n_clusters": n_total_clusters,
                "n_genes_per_cluster": n_markers_per_cluster,
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}