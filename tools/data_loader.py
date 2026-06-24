"""
data_loader.py — 读取 .h5ad 文件，缓存到 ADATA_CACHE，输出数据概览

不调用 LLM，只使用 Scanpy 读取并返回基本信息。
"""

import os
from datetime import datetime
import scanpy as sc
from tools import ADATA_CACHE


def load_data(adata_key_or_path: str, file_path: str | None = None) -> dict:
    """
    读取 .h5ad 文件并缓存。

    Args:
        adata_key_or_path: 缓存 key，如果 file_path 为 None 则作为文件路径使用
        file_path: .h5ad 文件路径（可选）

    Returns:
        {"status", "summary", "metrics", "error"}
    """
    # 兼容单参数调用：只传一个 path，自动生成 cache key
    if file_path is None:
        file_path = adata_key_or_path
        adata_key = f"adata_{abs(hash(file_path))}"
    else:
        adata_key = adata_key_or_path
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "summary": "",
            "metrics": {},
            "error": f"文件不存在: {file_path}",
        }

    try:
        adata = sc.read_h5ad(file_path)
        ADATA_CACHE[adata_key] = adata

        n_obs = adata.n_obs
        n_vars = adata.n_vars
        n_layers = len(adata.layers) if adata.layers else 0
        obs_cols = list(adata.obs.columns)
        var_cols = list(adata.var.columns[:10])  # 只显示前10个

        # 检查是否有 spatial 数据
        has_spatial = hasattr(adata, "obsm") and "spatial" in adata.obsm

        summary = (
            f"数据集已加载: {n_obs} 个细胞/spots × {n_vars} 个基因"
        )
        if has_spatial:
            summary += "，包含空间坐标信息"

        return {
            "status": "success",
            "summary": summary,
            "metrics": {
                "n_obs": n_obs,
                "n_vars": n_vars,
                "n_layers": n_layers,
                "has_spatial": has_spatial,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "summary": "",
            "metrics": {},
            "error": f"读取 .h5ad 失败: {e}",
        }


def get_data_overview(adata_key: str) -> dict:
    """获取已缓存数据的概览信息"""
    if adata_key not in ADATA_CACHE:
        return {"status": "error", "summary": "", "metrics": {}, "error": "数据未加载"}

    adata = ADATA_CACHE[adata_key]

    # 基本统计
    n_obs = adata.n_obs
    n_vars = adata.n_vars
    total_counts = adata.X.sum() if hasattr(adata.X, "sum") else 0
    pct_dropout = (adata.X == 0).sum() / (n_obs * n_vars) * 100 if hasattr(adata.X, "sum") else 0

    summary = (
        f"数据概览: {n_obs} 细胞 × {n_vars} 基因, "
        f"零表达比例: {pct_dropout:.1f}%"
    )

    return {
        "status": "success",
        "summary": summary,
        "metrics": {
            "n_obs": n_obs,
            "n_vars": n_vars,
            "total_counts": float(total_counts),
            "pct_dropout": float(pct_dropout),
        },
        "error": None,
    }