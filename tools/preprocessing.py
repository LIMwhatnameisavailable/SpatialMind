"""
preprocessing.py — 预处理（归一化、log 转换、HVG 筛选、标准化）

功能：
1. 全局缩放归一化 (sc.pp.normalize_total)
2. 对数转换 (sc.pp.log1p)
3. 高变基因识别 (sc.pp.highly_variable_genes)
4. 标准化 (sc.pp.scale)
5. HVG 可视化图
"""

from datetime import datetime
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, save_figure


def run_preprocessing(adata_key: str, **params) -> dict:
    """
    执行预处理流程。

    Args:
        adata_key: 缓存 key
        **params: target_sum, n_top_genes, flavor

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]
    target_sum = params.get("target_sum", 1e4)
    n_top_genes = params.get("n_top_genes", 2000)
    flavor = params.get("flavor", "seurat")

    try:
        # 归一化
        sc.pp.normalize_total(adata, target_sum=target_sum)
        # 对数转换
        sc.pp.log1p(adata)
        # HVG 筛选 — 如果数据尚未做 HVG subset
        if adata.n_vars > 5000 or "highly_variable" not in adata.var:
            sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, flavor=flavor)
            adata = adata[:, adata.var["highly_variable"]].copy()
        else:
            # 已经做过 HVG，使用现有标记
            if "highly_variable" in adata.var:
                n_selected = adata.var["highly_variable"].sum()
                if n_selected < adata.n_vars:
                    adata = adata[:, adata.var["highly_variable"]].copy()
        # 标准化
        sc.pp.scale(adata, max_value=10)

        ADATA_CACHE[adata_key] = adata

        # 生成 HVG 图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度

        # 1. 先创建画布
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        # 2. 再应用全局样式
        apply_global_style()
        # 3. 绘图
        if "highly_variable" in adata.var:
            hvg_counts = adata.var["highly_variable"].value_counts()
            axes[0].bar(["Not HVG", "HVG"], [hvg_counts.get(False, 0), hvg_counts.get(True, 0)], color=["gray", "red"])
            axes[0].set_title(f"HVG Selection (n={hvg_counts.get(True, 0)})")
            axes[0].set_ylabel("Gene count")
        else:
            axes[0].text(0.5, 0.5, "No HVG data available", ha="center", va="center", transform=axes[0].transAxes)
        sc.pl.scatter(adata, "n_genes_by_counts", "total_counts", ax=axes[1], show=False)
        # 4. 手动修复 scanpy 可能覆盖的样式
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)
        plt.tight_layout()
        # 5. 保存
        fig_path = f"outputs/figures/preprocess_{timestamp}.png"
        save_figure(fig, "outputs/figures", stem=f"preprocess_{timestamp}", dpi=150)
        plt.close(fig)

        summary = (
            f"预处理完成: 归一化(target_sum={target_sum}), "
            f"log转换, HVG筛选(n_top={n_top_genes}), 标准化"
        )

        return {
            "status": "success",
            "summary": summary,
            "figure_paths": [fig_path],
            "metrics": {
                "target_sum": target_sum,
                "n_top_genes": n_top_genes,
                "n_genes_after_hvg": adata.n_vars,
                "n_obs": adata.n_obs,
                "flavor": flavor,
            },
            "error": None,
        }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}