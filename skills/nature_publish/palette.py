"""
palette.py — Nature/Cell/Science 配色方案

提供三种期刊标准配色的色板，用于图表生成。
"""

# Nature 期刊经典配色
NATURE_PALETTE = [
    "#E64B35",  # 红
    "#4DBBD5",  # 蓝
    "#00A087",  # 绿
    "#3C5488",  # 深蓝
    "#F39B7F",  # 橙
    "#8491B4",  # 灰蓝
    "#91D1C2",  # 浅绿
    "#DC0000",  # 亮红
    "#7E6148",  # 棕
    "#B09C85",  # 米色
]

# Cell 期刊经典配色
CELL_PALETTE = [
    "#D7263D",  # 红
    "#1B9AAA",  # 青
    "#F46036",  # 橙
    "#2E4057",  # 深灰
    "#8DB600",  # 黄绿
    "#5A4A6A",  # 紫灰
    "#E2A76F",  # 杏色
    "#221D23",  # 黑
    "#B8D4E3",  # 浅蓝
    "#E8D6CB",  # 肤色
]

# Science 期刊经典配色
SCIENCE_PALETTE = [
    "#0072B5",  # 蓝
    "#BC3C29",  # 红
    "#20854E",  # 绿
    "#E18727",  # 橙
    "#7876B1",  # 紫
    "#FFDC91",  # 黄
    "#6F99AD",  # 灰蓝
    "#EE4C97",  # 粉
    "#868686",  # 灰
    "#D0C9C0",  # 米灰
]

JOURNAL_PALETTES = {
    "nature": NATURE_PALETTE,
    "cell": CELL_PALETTE,
    "science": SCIENCE_PALETTE,
}


def get_palette(journal: str = "nature", n_colors: int = 10) -> list[str]:
    """
    获取期刊配色方案。

    Args:
        journal: "nature" | "cell" | "science"
        n_colors: 需要的颜色数

    Returns:
        颜色列表
    """
    palette = JOURNAL_PALETTES.get(journal.lower(), NATURE_PALETTE)
    if n_colors <= len(palette):
        return palette[:n_colors]
    # 颜色不够时循环
    return [palette[i % len(palette)] for i in range(n_colors)]