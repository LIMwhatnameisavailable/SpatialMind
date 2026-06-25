
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
