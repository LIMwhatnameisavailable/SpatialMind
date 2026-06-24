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
