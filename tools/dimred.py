"""
dimred.py — 降维（PCA + UMAP）

功能：
1. PCA 降维（sc.tl.pca）
2. UMAP 降维（sc.tl.umap）
3. PCA 解释方差图和 UMAP 图
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, save_figure


def run_dimred(adata_key: str, **params) -> dict:
    """
    执行降维分析

    Args:
        adata_key: 缓存 key
        **params: n_pcs, n_neighbors, min_dist, random_state

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]
    n_pcs = params.get("n_pcs", 50)
    n_neighbors = params.get("n_neighbors", 15)
    min_dist = params.get("min_dist", 0.3)
    random_state = params.get("random_state", 42)

    try:
        # PCA
        sc.tl.pca(adata, n_comps=n_pcs, svd_solver="arpack", random_state=random_state)
        # 邻居图
        sc.pp.neighbors(adata, n_pcs=min(n_pcs, 30), n_neighbors=n_neighbors, random_state=random_state)
        # UMAP
        sc.tl.umap(adata, min_dist=min_dist, random_state=random_state)
        ADATA_CACHE[adata_key] = adata

        # 绘图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度

        # 1. 先创建画布
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        # 2. 再应用全局样式
        apply_global_style()
        # 3. 绘图
        # PCA 方差比（手动绘制，sc.pl.pca_variance_ratio 不支持 ax=）
        var_ratio = adata.uns["pca"]["variance_ratio"][:min(30, n_pcs)]
        axes[0].plot(range(1, len(var_ratio) + 1), var_ratio, "o-", markersize=3)
        axes[0].set_xlabel("PC")
        axes[0].set_ylabel("Variance ratio")
        axes[0].set_title("PCA Variance Ratio")
        sc.pl.umap(adata, ax=axes[1], show=False)
        # 4. 手动修复 scanpy 可能覆盖的样式
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)
        plt.tight_layout()
        # 5. 保存
        fig_path = f"outputs/figures/dimred_{timestamp}.png"
        save_figure(fig, "outputs/figures", stem=f"dimred_{timestamp}", dpi=150)
        plt.close(fig)

        return {
            "status": "success",
            "summary": f"降维完成: PCA({n_pcs} 主成分) → UMAP(min_dist={min_dist})",
            "figure_paths": [fig_path],
            "metrics": {
                "n_pcs": n_pcs,
                "pca_variance_ratio": float(adata.uns["pca"]["variance_ratio"][:5].sum()),
                "n_neighbors": n_neighbors,
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}