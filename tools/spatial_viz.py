"""
spatial_viz.py — 空间分布可视化

功能：
1. 细胞/spot 空间分布图（squidpy 或手动 scatter）
2. 基于 cluster 着色的空间分布图
3. 基因表达空间分布图
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, get_cluster_colors, save_figure


def run_spatial_viz(adata_key: str, **params) -> dict:
    """
    执行空间可视化。

    Args:
        adata_key: 缓存 key
        **params: color (着色方式), gene (指定基因), library_id
        * params also supports "spatial_key" (default "spatial")

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]
    color = params.get("color", None)
    gene = params.get("gene", None)

    try:
        # 检查是否有空间坐标
        if "spatial" not in adata.obsm:
            # 尝试找其他坐标
            spatial_key = None
            for key in adata.obsm.keys():
                if "spatial" in key.lower():
                    spatial_key = key
                    break
            if spatial_key is None:
                return {
                    "status": "error",
                    "summary": "",
                    "figure_paths": [],
                    "metrics": {},
                    "error": "数据中没有空间坐标信息",
                }
        else:
            spatial_key = "spatial"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度

        # 判断用 scanpy.pl.spatial 还是手动绘图
        fig_paths = []

        # 1. 基本空间分布图
        fig, ax = plt.subplots(figsize=(8, 8))
        apply_global_style()
        coordinates = adata.obsm[spatial_key]
        ax.scatter(coordinates[:, 0], coordinates[:, 1], s=1, c="steelblue", alpha=0.6)
        ax.set_title(f"Spatial Distribution ({adata.n_obs} spots)")
        ax.set_aspect("equal")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig1_path = f"outputs/figures/spatial_base_{timestamp}.png"
        save_figure(fig, "outputs/figures", stem=f"spatial_base_{timestamp}", dpi=150)
        plt.close(fig)
        fig_paths.append(fig1_path)

        # 2. 如果有聚类结果，按 cluster 着色
        cluster_keys = [k for k in adata.obs.keys() if k in ("leiden", "louvain", "clusters")]
        if cluster_keys:
            cluster_key = cluster_keys[0]
            fig, ax = plt.subplots(figsize=(9, 8))
            apply_global_style()
            clusters = adata.obs[cluster_key].values
            unique_clusters = np.unique(clusters)
            colors = get_cluster_colors(len(unique_clusters))
            for i, cl in enumerate(unique_clusters):
                mask = clusters == cl
                ax.scatter(
                    coordinates[mask, 0], coordinates[mask, 1],
                    s=3, c=[colors[i]], label=f"Cluster {cl}", alpha=0.7
                )
            ax.set_title(f"Spatial Distribution by {cluster_key}")
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
            ax.set_aspect("equal")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            fig2_path = f"outputs/figures/spatial_cluster_{timestamp}.png"
            save_figure(fig, "outputs/figures", stem=f"spatial_cluster_{timestamp}", dpi=150)
            plt.close(fig)
            fig_paths.append(fig2_path)

        # 3. 如果指定了基因，绘制基因表达空间分布
        if gene and gene in adata.var_names:
            fig, ax = plt.subplots(figsize=(8, 8))
            apply_global_style()
            gene_idx = list(adata.var_names).index(gene)
            expr = adata.X[:, gene_idx].toarray().flatten() if hasattr(adata.X, "toarray") else adata.X[:, gene_idx].flatten()
            scatter = ax.scatter(
                coordinates[:, 0], coordinates[:, 1],
                s=5, c=expr, cmap="viridis", alpha=0.7
            )
            plt.colorbar(scatter, ax=ax, label=f"{gene} expression")
            ax.set_title(f"Spatial Expression: {gene}")
            ax.set_aspect("equal")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            fig3_path = f"outputs/figures/spatial_gene_{gene}_{timestamp}.png"
            save_figure(fig, "outputs/figures", stem=f"spatial_gene_{gene}_{timestamp}", dpi=150)
            plt.close(fig)
            fig_paths.append(fig3_path)

        summary = f"空间可视化完成，共生成 {len(fig_paths)} 张图"

        return {
            "status": "success",
            "summary": summary,
            "figure_paths": fig_paths,
            "metrics": {
                "n_figures": len(fig_paths),
                "cluster_keys_found": cluster_keys,
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}