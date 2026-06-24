"""
panel_composer.py — 多子图排版

将多个独立生成的图表组合成 Figure 1a-f 风格的排版图。
"""

import os
from datetime import datetime
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from agent.state import AgentState


def compose_panels(state: AgentState) -> dict:
    """
    将 state.figures 中的图片组合成期刊风格的多子图排版。

    Args:
        state: AgentState

    Returns:
        {"panel_path": str, "n_panels": int}
    """
    figures = state.get("figures", {})
    if not figures:
        return {"panel_path": "", "n_panels": 0}

    step_order = ["qc", "preprocess", "dimred", "cluster", "spatial", "marker", "svg"]
    available_figs = []

    for step in step_order:
        if step in figures and os.path.exists(figures[step]):
            available_figs.append((step, figures[step]))

    if not available_figs:
        return {"panel_path": "", "n_panels": 0}

    n = len(available_figs)
    cols = min(3, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes_flat = [axes] if rows == 1 and cols == 1 else axes.flatten()

    for i, (step_name, fig_path) in enumerate(available_figs):
        if i < len(axes_flat):
            img = Image.open(fig_path)
            axes_flat[i].imshow(img)
            axes_flat[i].set_title(step_name.upper(), fontsize=12, fontweight="bold")
            axes_flat[i].axis("off")

    # 隐藏多余的子图
    for i in range(n, len(axes_flat)):
        axes_flat[i].axis("off")

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    panel_path = f"outputs/figures/panel_figure_{timestamp}.png"
    fig.savefig(panel_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return {"panel_path": panel_path, "n_panels": n, "panel_paths": [panel_path]}


def compose_spatial_panels(state: AgentState, ncols: int = 2) -> dict:
    """
    专门组合空间相关图形的排版。

    Args:
        state: AgentState

    Returns:
        {"panel_path": str, "n_panels": int}
    """
    figures = state.get("figures", {})
    spatial_figs = {k: v for k, v in figures.items() if "spatial" in k.lower()}

    if not spatial_figs:
        return {"panel_path": "", "n_panels": 0}

    return compose_panels(state)