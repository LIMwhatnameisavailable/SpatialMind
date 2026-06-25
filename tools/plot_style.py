"""
plot_style.py — 全局绘图样式模块

从 PLOT_GUIDE.md 第6节提取，提供统一的 matplotlib 样式配置。
所有 tools/ 和 skills/ 的绘图函数必须在开头调用 apply_global_style()。

用法:
    from tools.plot_style import apply_global_style, get_cluster_colors, save_figure
    apply_global_style()
"""

from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt


def apply_global_style():
    """在每个绘图模块顶部调用此函数，确保全局风格一致。"""
    plt.rcParams.update({
        # 字体
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        # 字号
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 11,
        "figure.titlesize": 14,
        # 坐标轴
        "axes.linewidth": 1.0,
        "axes.edgecolor": "#444444",
        "axes.facecolor": "white",
        "axes.labelcolor": "#333333",
        "axes.spines.top": False,
        "axes.spines.right": False,
        # 刻度
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 4.0,
        "ytick.major.size": 4.0,
        "xtick.minor.size": 2.0,
        "ytick.minor.size": 2.0,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        # 线条
        "lines.linewidth": 2.0,
        # 图例
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#CCCCCC",
        "legend.fancybox": False,
        # 图幅
        "figure.facecolor": "white",
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        # 网格
        "axes.grid": False,
        # 默认色循环（cluster_palette 前 6 色）
        "axes.prop_cycle": plt.cycler(color=[
            "#4A90D9", "#E64B35", "#2A9D8F",
            "#E9C46A", "#6A4C93", "#8B5E3C",
        ]),
    })


def apply_nature_style(journal: str = "nature"):
    """
    NaturePublishSkill 增强样式，在 apply_global_style() 之后调用。

    Args:
        journal: "nature" | "cell" | "science"
    """
    overrides = {
        "nature": {
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "lines.linewidth": 1.0,
            "figure.dpi": 150,
            "savefig.dpi": 600,
        },
        "cell": {
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "savefig.dpi": 600,
        },
        "science": {
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "savefig.dpi": 600,
        },
    }
    plt.rcParams.update(overrides.get(journal, overrides["nature"]))


# Cluster 着色方案（12 色，PLOT_GUIDE.md §1.1）
CLUSTER_PALETTE = [
    "#4A90D9", "#E64B35", "#2A9D8F", "#E9C46A",
    "#6A4C93", "#8B5E3C", "#1A3A5C", "#F4A261",
    "#A8DADC", "#457B9D", "#C77DFF", "#2D6A4F",
]


def get_cluster_colors(n_clusters: int) -> list:
    """
    返回适用于 cluster 着色的颜色列表。

    Args:
        n_clusters: 聚类数量

    Returns:
        十六进制色码列表，≤12 用 CLUSTER_PALETTE，>12 用 tab20
    """
    if n_clusters <= 12:
        return CLUSTER_PALETTE[:n_clusters]
    cmap = plt.colormaps.get_cmap("tab20", n_clusters)
    return [mpl.colors.to_hex(cmap(i)) for i in range(n_clusters)]


def save_figure(
    fig: plt.Figure,
    output_dir: str,
    stem: str,
    dpi: int = 300,
    formats: Optional[list[str]] = None,
):
    """
    保存图片为 PNG + SVG。

    Args:
        fig: matplotlib 图形对象
        output_dir: 输出目录
        stem: 文件名主干（不含扩展名）
        dpi: PNG 的 DPI（默认 300）
        formats: 保存格式列表，默认 ["png", "svg"]
    """
    if formats is None:
        formats = ["png", "svg"]
    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        fig.savefig(
            p / f"{stem}.{fmt}",
            dpi=dpi if fmt == "png" else "figure",
            format=fmt,
            bbox_inches="tight",
            facecolor="white",
        )

from datetime import datetime
import os


# ══════════════════════════════════════════════
# 前端显示辅助函数（由 app.py 导入，供 Tab2/Tab4 使用）
# ══════════════════════════════════════════════

def get_figure_meta(filename: str) -> tuple:
    """
    从文件名解析图表类型和简要说明。

    Args:
        filename: 图片文件名，如 "qc_violin_n_genes_20260625.png"

    Returns:
        (chart_type, description)，均为字符串，未匹配时返回 ("图表", "")
    """
    FIGURE_META = {
        "qc_violin_n_genes":       ("小提琴图", "每细胞基因数分布"),
        "qc_violin_total_counts":  ("小提琴图", "总UMI计数分布"),
        "qc_violin_pct_mt":        ("小提琴图", "线粒体基因比例分布"),
        "qc_scatter_genes_counts": ("散点图",   "基因数与总计数关系"),
        "preprocess_hvg_bar":      ("柱状图",   "高变基因筛选结果"),
        "preprocess_scatter":      ("散点图",   "预处理后基因数与总计数关系"),
        "dimred_pca_variance":     ("折线图",   "PCA方差解释比"),
        "dimred_umap":             ("UMAP图",   "UMAP降维可视化"),
        "cluster_leiden":          ("UMAP图",   "Leiden聚类结果"),
        "cluster_louvain":         ("UMAP图",   "Louvain聚类结果"),
        "spatial_distribution":    ("散点图",   "细胞/spot空间分布"),
        "spatial_cluster":         ("散点图",   "聚类着色的空间分布"),
        "spatial_gene":            ("散点图",   "基因表达空间分布"),
        "marker_umap":             ("UMAP图",   "Marker基因UMAP分布"),
        "svg_moran_i":             ("条形图",   "Moran's I空间可变基因"),
        "panel_figure":            ("组合图",   "多子图排版"),
    }

    name = filename.replace(".png", "").replace(".svg", "")
    parts = name.split("_")
    while parts and parts[-1].isdigit():
        parts.pop()
    key = "_".join(parts)
    return FIGURE_META.get(key, ("图表", ""))


def get_step_display_name(step: str) -> str:
    """返回分析步骤的中文显示名"""
    STEP_NAMES = {
        "data_load":    "数据加载",
        "qc":           "QC质控",
        "preprocess":   "预处理",
        "dimred":       "降维",
        "cluster":      "聚类",
        "spatial":      "空间可视化",
        "marker":       "Marker基因",
        "svg":          "空间可变基因",
    }
    return STEP_NAMES.get(step, step.upper())



def _infer_step_from_filename(filename: str) -> str:
    """从图片文件名推断步骤名"""
    fname = filename.lower()
    step_map = {
        "qc": "qc",
        "preprocess": "preprocess",
        "pca": "dimred",
        "umap": "dimred",
        "dimred": "dimred",
        "cluster": "cluster",
        "leiden": "cluster",
        "louvain": "cluster",
        "spatial": "spatial",
        "marker": "marker",
        "deg": "marker",
        "svg": "svg",
        "data_load": "data_load",
        "data_loader": "data_load",
    }
    for key, step in step_map.items():
        if key in fname:
            return step
    return "other"


def manage_session_figures(session_id: str, keep_n: int = 2) -> str:
    """
    管理 session 的图文件目录。

    在 outputs/figures/<session_id>/ 下创建以时间戳命名的 run 目录，
    并清理该 session 下过旧的 run 目录（仅保留最近 keep_n 个）。

    Args:
        session_id: 会话 ID
        keep_n: 保留的 run 目录数量

    Returns:
        当前 run 目录的路径字符串
    """
    base = Path("outputs/figures") / session_id
    base.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    # 清理旧 run 目录
    all_runs = sorted(
        [d for d in base.iterdir() if d.is_dir()],
        reverse=True,
    )
    for old_dir in all_runs[keep_n:]:
        import shutil
        shutil.rmtree(old_dir, ignore_errors=True)

    return str(run_dir)


def discover_session_figures(session_id: str) -> list:
    """
    发现指定 session 下的所有图文件。

    Args:
        session_id: 会话 ID

    Returns:
        按 mtime 倒序的 dict 列表，每个 dict 包含 path/name/mtime
    """
    base = Path("outputs/figures") / session_id
    if not base.exists():
        return []

    results = []
    for run_dir in sorted(base.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        for f in sorted(run_dir.glob("*.png"), reverse=True):
            results.append({
                "path": str(f),
                "name": f.name,
                "mtime": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    return results
