# 🧬 SpatialMind

> 一个基于 LangGraph 的空间转录组分析 Agent，支持自然语言驱动的分析流程，输出发表级图表与生物学洞察。

![Python](https://img.shields.io/badge/Python-3.10-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 核心特性

- 🗣️ **自然语言驱动**：直接描述分析需求，Agent 自动规划执行步骤
- 🔄 **LangGraph 工作流**：可视化的"规划—执行—检查—修正"循环，执行过程透明可见
- 🎨 **NaturePublishSkill**：一键输出 Nature/Cell 级别图表、图注、Methods、Cover Letter 和 Word 论文
- 🧠 **BioInsightSkill**：自动 cluster 命名、文献阅读、空间叙事与下一步分析建议
- 📦 **多数据类型支持**：Stereo-seq、10x Visium 开箱即用
- 💾 **断点续传**：基于 SqliteSaver 的会话持久化，关闭后可恢复分析进度

---

## 🚀 快速开始

### 1. 安装依赖

```bash
git clone https://github.com/your_username/SpatialMind.git
cd SpatialMind
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 PPIO API Key
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

### 🌐 在线访问
本项目已部署于阿里云服务器，可直接访问：
**http://47.101.68.210:8501**

---

## 📊 支持的分析功能

### 基础功能
| 功能 | 说明 |
|------|------|
| 数据读取与概览 | 读取 .h5ad，展示 obs/var 基本信息 |
| 质量控制 | 细胞/基因过滤、线粒体基因过滤、QC图 |
| 基础预处理 | 归一化、log转换、HVG筛选、标准化 |
| 降维与聚类 | PCA、UMAP、Leiden/Louvain |
| 空间可视化 | 细胞空间分布、cluster分布、基因表达分布 |
| Marker Gene分析 | 差异表达、点图、热图 |

### 扩展功能
| 功能 | 说明 |
|------|------|
| 空间可变基因（SVG） | 识别具有空间表达模式的基因 |
| 多数据类型 | Stereo-seq / 10x Visium 自动识别 |
| 交互式图表 | Plotly 可缩放图表 |

---

## 🎨 NaturePublishSkill

将分析结果一键升级为发表级输出：

- **配色方案**：内置 Nature、Cell、Science 三种期刊标准配色
- **多子图排版**：自动生成 Figure 1a-f 风格组合图
- **图注生成**：符合期刊投稿规范的英文图注
- **Methods 段落**：根据实际运行参数自动生成
- **语言润色**：将分析摘要润色为学术英文
- **Cover Letter**：基于分析结果生成投稿信
- **Word 导出**：生成完整论文格式 .docx 文件
- **HTML 报告**：生成独立可分享的 HTML 分析报告

---

## 🧠 BioInsightSkill

提供超越数据本身的生物学洞察：

- **Cluster 命名**：结合 marker genes 与 CellMarker 数据库自动命名
- **空间叙事**：将空间分布数据转化为可读的生物学描述
- **QC 解读**：判断 QC 指标是否在正常范围并给出建议
- **文献阅读**：上传 PDF 文献，提取关键发现并与你的数据关联
- **下一步建议**：基于当前分析状态推荐后续分析方向
- **Key Findings**：提炼分析中的关键发现（标注 AI 生成，仅供参考）

---

## 🏗️ Agent 架构

```
用户自然语言输入
        ↓
  ┌─────────────────────────────────────┐
  │  intent_parser → planner            │
  │       ↓          (ThinkingBlock)    │
  │  executor → checker                 │
  │    ↑    ↓ pass    ↓ fail            │
  │    │  explainer  error_handler      │
  │    └────────────────┘  loop        │
  │           ↓ all done               │
  │      skill_invoker → END           │
  └─────────────────────────────────────┘
        ↓              ↓
   Tools Layer     Skills Layer
  (Scanpy/纯代码)  (LLM增强输出)
```

LangGraph 执行路径在 Streamlit 的"Agent思考"标签页中实时可见。

---

## 📁 数据准备

### 推荐数据集（作业指定）
**GSE278603** — Digital reconstruction of full embryos during early mouse organogenesis

```bash
# 数据下载（选择其中一个胚胎文件即可快速测试）
# 文件名格式：GSM9046243_Embryo_E7.5_stereo_*.h5ad
# 下载地址：https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278603
```

### 示例数据（快速体验）
仓库包含 10x Visium 小鼠脑示例数据，无需下载即可运行：
```bash
# 示例数据位于 data/data/anndata/visium_hne_adata.h5ad
```

---

## 🔧 环境要求

- Python 3.10+
- PPIO API Key（用于 LLM 功能）
- 内存建议 16GB+（处理大型 h5ad 文件）

---

## 📝 项目结构

```
SpatialMind/
├── app.py              # Streamlit 前端入口
├── agent/              # LangGraph Agent 核心
├── tools/              # Scanpy 分析工具层
├── skills/             # NaturePublishSkill + BioInsightSkill
├── data/               # 数据目录
└── outputs/            # 生成的图表与报告
```

详细架构说明见 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ⚠️ 免责声明

BioInsightSkill 生成的生物学解读内容由 AI 生成，仅供参考，不构成科学结论。请结合领域知识独立判断。

---

## 📧 致谢

本项目为东南大学计算生物学课程期末作业，使用 GSE278603 数据集。
