# SpatialMind 数据字段说明

> 本文件说明 `data/schema/` 中的字段定义，适用于 Stereo-seq 和 10x Visium 数据。

---

## 一、Stereo-seq（stereo_schema.json）

### obs 字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `barcode` | string | 细胞/spot 唯一标识 |
| `n_genes_by_counts` | int | 检测到的基因数 |
| `total_counts` | float | UMI 总数 |
| `pct_counts_mt` | float | 线粒体基因占比 (%) |
| `n_counts` | float | 与 total_counts 同义 |
| `leiden` | categorical | Leiden 聚类结果 |
| `louvain` | categorical | Louvain 聚类结果 |
| `cluster` | categorical | 通用聚类标签 |

### var 字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `gene_ids` | string | 基因 ID（Ensembl） |
| `n_cells_by_counts` | int | 表达该基因的细胞数 |
| `mean_counts` | float | 平均表达量 |
| `pct_dropout_by_counts` | float | 零表达比例 |
| `highly_variable` | bool | 是否高变基因 |
| `mt` | bool | 是否线粒体基因 |

### obsm 字段

| 键名 | 形状 | 说明 |
|------|------|------|
| `spatial` | (n_obs, 2) | 空间坐标 (x, y) |
| `X_pca` | (n_obs, n_pcs) | PCA 降维坐标 |
| `X_umap` | (n_obs, 2) | UMAP 降维坐标 |

### uns 字段

| 键名 | 说明 |
|------|------|
| `pca` | PCA 结果（含 variance_ratio） |
| `neighbors` | 邻居图参数 |
| `umap` | UMAP 参数 |
| `leiden` / `louvain` | 聚类参数 |
| `rank_genes_groups` | Marker gene 分析结果 |
| `moranI` | 空间自相关分析结果（Squidpy） |

---

## 二、10x Visium（visium_schema.json）

### 与 Stereo-seq 的区别

- **空间分辨率不同**: Visium 是 55μm 直径的 spots（每个 spot 含 1-10 个细胞），Stereo-seq 是亚细胞分辨率（500nm-2μm）
- **数据形状**: Visium 通常 ~5,000 spots × ~20,000 genes，Stereo-seq ~100,000+ bins × ~20,000 genes
- **图像数据**: Visium 包含组织切片 H&E 染色图（tissue_hires_image.png, tissue_lowres_image.png）

### obs 额外字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `in_tissue` | int (0/1) | 是否位于组织区域内 |
| `array_row` | int | 芯片行坐标 |
| `array_col` | int | 芯片列坐标 |
| `pxl_row_in_fullres` | float | 高分辨率图像行像素 |
| `pxl_col_in_fullres` | float | 高分辨率图像列像素 |

### spatial 目录结构

```
spatial/
├── tissue_hires_image.png      # 高分辨率组织图像
├── tissue_lowres_image.png     # 低分辨率组织图像
├── scalefactors_json.json      # 缩放因子
├── tissue_positions_list.csv   # spot 位置信息
└── aligned_fiducials.jpg       # 基准标记对齐图
```

---

## 三、AnnData 核心属性

```python
# 使用 Scanpy 读取后
adata = sc.read_h5ad("path.h5ad")

# 基本属性
adata.X          # 表达矩阵 (n_obs × n_vars)，通常为稀疏矩阵
adata.obs        # 细胞/spot 元数据 DataFrame
adata.var        # 基因元数据 DataFrame
adata.obsm       # 细胞级多维数组（PCA, UMAP, spatial 坐标）
adata.varm       # 基因级多维数组
adata.uns        # 非结构化数据字典（分析结果）
adata.layers     # 多层表达数据（raw, normalized, scaled 等）
adata.obsp       # 细胞间图结构（邻接矩阵等）
```

---

## 四、数据加载流程

```python
# 标准加载流程
import scanpy as sc

# 1. 读取 .h5ad
adata = sc.read_h5ad("data/example.h5ad")

# 2. 自动检测数据类型
if "spatial" in adata.obsm:
    # 检查坐标范围判断 Visium vs Stereo-seq
    coords = adata.obsm["spatial"]
    is_stereo = coords.max() > 5000  # Stereo-seq 坐标范围通常更大
    data_type = "stereo" if is_stereo else "visium"

# 3. 数据概览
print(adata)
# AnnData object with n_obs × n_vars = 5000 × 20000
#     obs: 'barcode', 'n_genes_by_counts', 'total_counts'
#     var: 'gene_ids', 'n_cells_by_counts', 'mt'
#     obsm: 'spatial', 'X_pca'
#     uns: 'pca', 'neighbors'
```

---

## 五、注意事项

1. **不够 `raw` 属性**: 部分数据有 `adata.raw`（原始未归一化数据），部分没有
2. **batch 效应**: 多切片数据可能有 batch 效应，需 `sc.pp.combat()` 或 `sc.external.pp.harmony_integrate()`
3. **稀疏矩阵**: `adata.X` 通常是 `scipy.sparse.csr_matrix`，需用 `.toarray()` 转为稠密
4. **坐标参考系**: Stereo-seq 坐标可能是纳米单位（如 500000），Visium 是像素坐标（通常 <2000）