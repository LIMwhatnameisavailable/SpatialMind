"""
clustering.py — Leiden/Louvain 聚类

功能：
1. Leiden 聚类（sc.tl.leiden）
2. Louvain 聚类（sc.tl.louvain）
3. UMAP 着色聚类结果

注意事项（PLOT_GUIDE §9 禁止事项）：
- 禁止对同一 adata 对象多次调用 — 会导致 cluster 列被覆盖、图表内容重复。
  本函数会自动检测现有 cluster 列，若已有相同 method 且 resolution 相同则跳过。
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, get_cluster_colors, save_figure


def run_clustering(adata_key: str, **params) -> dict:
    """
    执行聚类分析。

    Args:
        adata_key: 缓存 key
        **params: method ("leiden"|"louvain"), resolution

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]
    method = params.get("method", "leiden")
    resolution = params.get("resolution", 0.5)

    try:
        # 确保有邻居图和 UMAP
        if "neighbors" not in adata.uns:
            sc.pp.neighbors(adata, random_state=42)

        cluster_key = "leiden" if method == "leiden" else "louvain"

        # === 防重复执行保护 ===
        # 如果 cluster_key 已存在且 resolution 相同，跳过重新计算
        if cluster_key in adata.obs:
            prev_resolution = adata.uns.get("leiden_resolution" if method == "leiden" else "louvain_resolution", None)
            if prev_resolution == resolution:
                n_clusters = adata.obs[cluster_key].nunique()
                summary = (
                    f"聚类已存在: {method.capitalize()} (resolution={resolution}, "
                    f"{n_clusters} clusters)，跳过重复计算"
                )
                # 仍尝试出图
                has_umap = "X_umap" in adata.obsm
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度
                if has_umap:
                    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                    apply_global_style()
                    sc.pl.umap(adata, color=cluster_key, ax=axes[0], show=False, legend_loc="on data")
                    sc.pl.umap(adata, color=cluster_key, ax=axes[1], show=False, legend_loc="right margin")
                    for ax in axes:
                        ax.spines["top"].set_visible(False)
                        ax.spines["right"].set_visible(False)
                    plt.tight_layout()
                else:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    apply_global_style()
                    sc.pl.umap(adata, color=cluster_key, ax=ax, show=False)
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)
                    plt.tight_layout()
                fig_path = f"outputs/figures/clustering_{timestamp}.png"
                save_figure(fig, "outputs/figures", stem=f"clustering_{timestamp}", dpi=150)
                plt.close(fig)
                return {
                    "status": "success",
                    "summary": summary,
                    "figure_paths": [fig_path],
                    "metrics": {"method": method, "resolution": resolution, "n_clusters": n_clusters, "skipped": True},
                    "error": None,
                }

        if method == "leiden":
            sc.tl.leiden(adata, resolution=resolution, key_added=cluster_key)
            adata.uns["leiden_resolution"] = resolution
        else:
            sc.tl.louvain(adata, resolution=resolution, key_added=cluster_key)
            adata.uns["louvain_resolution"] = resolution

        # 如果已有 UMAP，画 UMAP 着色聚类
        has_umap = "X_umap" in adata.obsm

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度

        n_clusters = adata.obs[cluster_key].nunique()

        if has_umap:
            # 1. 先创建画布
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            # 2. 再应用全局样式
            apply_global_style()
            # 3. 绘图时显式传入 ax
            sc.pl.umap(adata, color=cluster_key, ax=axes[0], show=False, legend_loc="on data")
            sc.pl.umap(adata, color=cluster_key, ax=axes[1], show=False, legend_loc="right margin")
            # 4. 手动修复 scanpy 可能覆盖的样式
            for ax in axes:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
            plt.tight_layout()
        else:
            # 1. 先创建画布
            fig, ax = plt.subplots(figsize=(8, 6))
            # 2. 再应用全局样式
            apply_global_style()
            # 3. 绘图
            sc.pl.umap(adata, color=cluster_key, ax=ax, show=False)
            # 4. 手动修复
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tight_layout()

        # 5. 保存
        fig_path = f"outputs/figures/clustering_{timestamp}.png"
        save_figure(fig, "outputs/figures", stem=f"clustering_{timestamp}", dpi=150)
        plt.close(fig)

        ADATA_CACHE[adata_key] = adata

        summary = (
            f"聚类完成: {method.capitalize()} (resolution={resolution}), "
            f"共 {n_clusters} 个 cluster"
        )

        return {
            "status": "success",
            "summary": summary,
            "figure_paths": [fig_path],
            "metrics": {
                "method": method,
                "resolution": resolution,
                "n_clusters": n_clusters,
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}