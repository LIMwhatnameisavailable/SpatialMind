"""
svg.py — 空间可变基因（SVG）分析

功能：
1. 使用 Squidpy 的 spatial autocorrelation (Moran's I) 识别 SVG
2. 可视化表达相关性矩阵和空间模式
"""

from datetime import datetime
import scanpy as sc
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tools import ADATA_CACHE
from tools.plot_style import apply_global_style, save_figure

try:
    import squidpy as sq
    HAS_SQUIDPY = True
except ImportError:
    HAS_SQUIDPY = False


def run_svg(adata_key: str, **params) -> dict:
    """
    执行空间可变基因分析。

    Args:
        adata_key: 缓存 key
        **params: n_top_svgs, spatial_key

    Returns:
        {"status", "summary", "figure_paths", "metrics", "error"}
    """
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": "数据未加载"}

    if not HAS_SQUIDPY:
        return {
            "status": "error",
            "summary": "",
            "figure_paths": [],
            "metrics": {},
            "error": "Squidpy 未安装，无法执行 SVG 分析",
        }

    adata = ADATA_CACHE[adata_key]
    n_top_svgs = params.get("n_top_svgs", 10)
    spatial_key = params.get("spatial_key", "spatial")

    # 检查空间坐标
    if spatial_key not in adata.obsm:
        alt_keys = [k for k in adata.obsm.keys() if "spatial" in k.lower()]
        if alt_keys:
            spatial_key = alt_keys[0]
        else:
            return {
                "status": "error",
                "summary": "",
                "figure_paths": [],
                "metrics": {},
                "error": "数据中没有空间坐标信息",
            }

    try:
        # 计算空间邻居图
        sq.gr.spatial_neighbors(adata, spatial_key=spatial_key, coord_type="generic")

        # 计算 Moran's I
        sq.gr.spatial_autocorr(
            adata,
            mode="moran",
            genes=adata.var_names[:100],  # 前 100 个基因
            n_perms=100,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]  # ms 精度
        fig_paths = []

        # 1. 查看 Moran's I 结果
        if "moranI" in adata.uns:
            moran_results = adata.uns["moranI"]
            top_genes = moran_results.sort_values("I", ascending=False).head(n_top_svgs)

            # 1. 先创建画布
            fig, ax = plt.subplots(figsize=(10, 6))
            # 2. 再应用全局样式
            apply_global_style()
            # 3. 绘图（ax.barh 是 matplotlib 原生，不需要手动修复 spines）
            ax.barh(range(len(top_genes)), top_genes["I"].values)
            ax.set_yticks(range(len(top_genes)))
            ax.set_yticklabels(top_genes.index)
            ax.set_xlabel("Moran's I")
            ax.set_title(f"Top {n_top_svgs} Spatial Variable Genes")
            # 4. 手动修复样式
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            fig.tight_layout()
            # 5. 保存
            fig1_path = f"outputs/figures/svg_top_{timestamp}.png"
            save_figure(fig, "outputs/figures", stem=f"svg_top_{timestamp}", dpi=150)
            plt.close(fig)
            fig_paths.append(fig1_path)

            summary = (
                f"SVG 分析完成: 在 {len(adata.var_names[:100])} 个基因中计算 Moran's I, "
                f"Top 基因: {', '.join(top_genes.index[:3])}"
            )

            return {
                "status": "success",
                "summary": summary,
                "figure_paths": fig_paths,
                "metrics": {
                    "n_genes_tested": min(100, adata.n_vars),
                    "n_svgs_found": n_top_svgs,
                    "top_genes": list(top_genes.index[:5]),
                    "top_moran_i": float(top_genes["I"].iloc[0]),
                },
                "error": None,
            }
        else:
            return {
                "status": "error",
                "summary": "",
                "figure_paths": [],
                "metrics": {},
                "error": "Moran's I 计算未返回结果",
            }
    except Exception as e:
        return {"status": "error", "summary": "", "figure_paths": [], "metrics": {}, "error": str(e)}