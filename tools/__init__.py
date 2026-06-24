"""
Tools 包 — 纯 Scanpy/Squidpy 分析工具，禁止调用 LLM。

全局 ADATA_CACHE 用于缓存 AnnData 对象（避免存入 AgentState）。
"""

from typing import Any
import anndata

# 全局 AnnData 缓存: {adata_cache_key: AnnData}
ADATA_CACHE: dict[str, anndata.AnnData] = {}