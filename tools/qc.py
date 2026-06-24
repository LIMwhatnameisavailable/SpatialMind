"""
qc.py — 质量控制和 QC 图

功能：
1. QC 指标计算（线粒体基因比例、细胞/基因过滤）
2. QC 小提琴图
3. 过滤结果统计
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, save_figure


def run_qc(adata_key: str, **params) -> dict:
    """
    执行 QC 分析。

    Args:
        adata_key: 缓存 key
        **params: min_genes, min_cells, max_pct_mt

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]
    min_genes = params.get("min_genes", 200)
    min_cells = params.get("min_cells", 3)
    max_pct_mt = params.get("max_pct_mt", 20)

    try:
        # 计算 QC 指标
        adata.var["mt"] = adata.var_names.str.startswith("MT-") | adata.var_names.str.startswith("mt-")
        sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

        n_before = adata.n_obs

        # 过滤
        sc.pp.filter_cells(adata, min_genes=min_genes)
        sc.pp.filter_genes(adata, min_cells=min_cells)
        adata = adata[adata.obs.pct_counts_mt < max_pct_mt, :].copy()
        ADATA_CACHE[adata_key] = adata

        n_after = adata.n_obs
        n_filtered = n_before - n_after

        # QC 图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度

        # 1. 先创建画布
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        # 2. 再应用全局样式（确保 rcParams 在创建 figure 后被设置，防 scanpy 覆盖）
        apply_global_style()
        # 3. 绘图时显式传入 ax
        sc.pl.violin(adata, "n_genes_by_counts", ax=axes[0, 0], show=False)
        sc.pl.violin(adata, "total_counts", ax=axes[0, 1], show=False)
        sc.pl.violin(adata, "pct_counts_mt", ax=axes[1, 0], show=False)
        sc.pl.scatter(adata, "total_counts", "n_genes_by_counts", ax=axes[1, 1], show=False)
        # 4. 手动修复 scanpy 可能覆盖的样式
        for ax in axes.flat:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        plt.tight_layout()
        # 5. 保存
        fig_path = f"outputs/figures/qc_{timestamp}.png"
        save_figure(fig, "outputs/figures", stem=f"qc_{timestamp}", dpi=150)
        plt.close(fig)

        summary = (
            f"QC 完成: 过滤前 {n_before} 细胞, "
            f"过滤后 {n_after} 细胞, "
            f"过滤比例 {(n_filtered/n_before)*100:.1f}%"
        )

        return {
            "status": "success",
            "summary": summary,
            "figure_paths": [fig_path],
            "metrics": {
                "n_before": n_before,
                "n_after": n_after,
                "n_filtered": n_filtered,
                "filter_ratio": round(n_filtered / n_before, 4) if n_before > 0 else 0,
                "n_genes": adata.n_vars,
                "mean_counts_per_cell": float(adata.obs.total_counts.mean()),
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}