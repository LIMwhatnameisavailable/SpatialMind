# SpatialMind 开发进度

## 总览

- **项目**: SpatialMind — 基于 LangGraph 的空间转录组分析 Agent
- **开始日期**: 2026-06-23
- **目标**: 实现完整的自然语言驱动的空间转录组分析流程

---

## 完成进度

### ✅ Phase 1: 项目骨架 (2026-06-23)

| 步骤 | 状态 | 说明 |
|------|------|------|
| 创建目录结构 | ✅ | 完整遵循 CLAUDE.md 规范的目录树 |
| `__init__.py` 包文件 | ✅ | agent/, tools/, skills/, tests/ 及其子包 |
| `requirements.txt` | ✅ | 所有依赖已定义并安装到 boneage 环境 |
| 环境配置 | ✅ | PPIO API Key 已验证，LLM 调用测试通过 |

### ✅ Phase 2: Agent 核心 (2026-06-23)

| 组件 | 状态 | 文件 |
|------|------|------|
| `state.py` | ✅ | AgentState TypedDict 定义 |
| `llm_client.py` | ✅ | LLM 统一调用封装（Anthropic SDK → PPIO） |
| `graph.py` | ✅ | LangGraph 图定义（7 节点 + 条件边 + SqliteSaver） |
| `nodes/intent_parser.py` | ✅ | 规则引擎解析用户输入 |
| `nodes/planner.py` | ✅ | 调用 LLM (ThinkingBlock) 生成分析计划 |
| `nodes/executor.py` | ✅ | 动态导入 tools 执行分析步骤 |
| `nodes/checker.py` | ✅ | LLM 检查结果合理性 |
| `nodes/explainer.py` | ✅ | LLM 生成结果解释 |
| `nodes/error_handler.py` | ✅ | 重试/跳过决策 |
| `nodes/skill_invoker.py` | ✅ | 调用 Skills 层 |

### ✅ Phase 3: Tools 层 (2026-06-23)

| 工具 | 状态 | 文件 |
|------|------|------|
| `data_loader.py` | ✅ | .h5ad 读取 + ADATA_CACHE 缓存 |
| `qc.py` | ✅ | QC 指标计算 + 小提琴图 |
| `preprocessing.py` | ✅ | 归一化/log/HVG/scale |
| `dimred.py` | ✅ | PCA + UMAP |
| `clustering.py` | ✅ | Leiden/Louvain 聚类 |
| `spatial_viz.py` | ✅ | 空间分布可视化（含手动 scatter） |
| `marker_genes.py` | ✅ | 差异表达分析 + 点图/热图 |
| `svg.py` | ✅ | Squidpy Moran's I 空间可变基因 |

### ✅ Phase 4: Skills 层 (2026-06-23)

| 模块 | 状态 | 文件 |
|------|------|------|
| NaturePublish: `palette.py` | ✅ | Nature/Cell/Science 配色 |
| NaturePublish: `panel_composer.py` | ✅ | 多子图排版 |
| NaturePublish: `caption_writer.py` | ✅ | LLM 图注生成 |
| NaturePublish: `methods_writer.py` | ✅ | LLM Methods 段落 |
| NaturePublish: `language_polish.py` | ✅ | LLM 语言润色 |
| NaturePublish: `cover_letter.py` | ✅ | LLM Cover Letter |
| NaturePublish: `word_exporter.py` | ✅ | python-docx 导出 |
| NaturePublish: `html_report.py` | ✅ | HTML 报告生成 |
| BioInsight: `cluster_namer.py` | ✅ | LLM + marker genes 命名 |
| BioInsight: `spatial_story.py` | ✅ | LLM 空间叙事 |
| BioInsight: `qc_interpreter.py` | ✅ | LLM QC 解读 |
| BioInsight: `next_step.py` | ✅ | LLM 下一步建议 |
| BioInsight: `lit_reader.py` | ✅ | pypdf + LLM 文献阅读 |
| BioInsight: `insight_extractor.py` | ✅ | LLM 关键发现 |

### ✅ Phase 5: 前端 (2026-06-23)

| 组件 | 状态 | 说明 |
|------|------|------|
| `app.py` | ✅ | Streamlit 4-Tab 界面 |
| 侧边栏 | ✅ | 文件上传 + 参数设置 + Skills 开关 |
| Tab1: 分析对话 | ✅ | 聊天界面 + Agent 实时执行 |
| Tab2: 分析结果 | ✅ | 步骤选择 + 图表展示 + 解释 |
| Tab3: Agent 思考 | ✅ | 执行路径可视化 + ThinkingBlock |
| Tab4: 导出中心 | ✅ | HTML/Word/图表下载 |

### ✅ Phase 6: 文档 (2026-06-23)

| 文档 | 状态 | 说明 |
|------|------|------|
| `ARCHITECTURE.md` | ✅ | 系统架构与节点设计 |
| `SKILLS.md` | ✅ | Skills 开发规范与接口 |
| `PROMPTS.md` | ✅ | 所有 LLM Prompt 模板 |
| `DATA_SCHEMA.md` | ✅ | 数据字段说明 |
| `README.md` | ✅ | 项目对外展示 |
| `stereo_schema.json` | ✅ | Stereo-seq 字段定义 |
| `visium_schema.json` | ✅ | Visium 字段定义 |

### ⏳ Phase 7: 测试与验证 (待完成)

| 项目 | 状态 | 说明 |
|------|------|------|
| 单元测试 Tools | ⏳ | 用 mock 数据测试 8 个工具 |
| 单元测试 Skills | ⏳ | 测试 Skills 模块 |
| 集成测试 Graph | ⏳ | LangGraph 全流程测试 |
| 真实数据运行 | ⏳ | 在 GSE278603 数据集上运行 |
| Streamlit 手动测试 | ⏳ | UI 交互验证 |

### ✅ Phase 8: 可视化规范与外部库集成 (2026-06-24)

| 项目 | 状态 | 说明 |
|------|------|------|
| 提取绘图样式模块 | ✅ | `tools/plot_style.py` — 含 `apply_global_style()`, `get_cluster_colors()`, `save_figure()`, `CLUSTER_PALETTE` |
| 修复 clustering 重复执行 bug | ✅ | ① clustering.py 增加防重复执行保护（检测已有 cluster 列 + resolution）；② 所有工具的时间戳改为毫秒精度防覆盖；③ error_handler.py 增加 retry_count 递增（之前遗漏导致重试时进入无限循环） |
| 引入 ClawBio 外部库 | ✅ | D:\SEU\AI tech\ClawBio — 88个生信技能。借鉴 `sample-qc-triage` 的 QC 决策逻辑和 `scrna-orchestrator` 的流程组织 |
| 引入 NatureSkills 外部库 | ✅ | D:\SEU\AI tech\nature-skills — `nature-figure` 的 figure contract 方法论、`nature-polishing` 的句式库、`nature-writing` 的章节架构 |
| 所有 tools 绘图函数改用 plot_style.apply_global_style() | ✅ | qc.py / preprocessing.py / dimred.py / clustering.py / spatial_viz.py / marker_genes.py / svg.py 均已添加 |
| 更新 CLAUDE.md 和 SKILLS.md | ✅ | CLAUDE.md 新增2条禁止事项 + PLOT_GUIDE.md 引用；SKILLS.md 新增"外部库集成说明"章节 |
| 清理 outputs/figures/ 实验图，建立归档目录结构 | ✅ | 删除6月23日33张旧图，创建 archive/{qc,dimred,cluster,spatial,preprocess,marker,svg,panel} 子目录 |
| 修复 apply_global_style() 调用顺序（scanpy 覆盖问题） | ✅ | 6个工具全部修复为：先 subplots() → apply_global_style() → 绘图(ax=) → 手动修复 spine → save_figure() → plt.close() |

### ⏳ Phase 9: LangGraph 端到端集成测试

| 步骤 | 状态 | 说明 |
|------|------|------|
| 9.1 最小闭环测试 | ✅ | data_load 单步执行成功，图正常结束（修复了数据未加载的无限循环 + planner 缺失 data_load 步骤的 bug） |
| 9.2 完整Loop测试 | ✅ | 6步全流程执行成功（data_load→qc→preprocess→dimred→cluster→spatial），每步均有图表+解释，Skills 输出正常 |
| 9.3 NatureSkills prompt 集成 | ✅ | language_polish / caption_writer / methods_writer 三个skill已从 PROMPTS.md 加载经过NatureSkills增强的prompt；新增 agent/prompts_loader.py 模块 |
| 9.4 Streamlit 前端联调 | ✅ | 4个Tab全部可用 |
| 9.5 Stereo-seq 数据端到端测试 | ⏳ | |
| 9.6 最终集成测试 + README 截图更新 | ⏳ | |

---

## 下一步计划

1. 编写单元测试（`tests/test_tools.py`, `tests/test_skills.py`, `tests/test_graph.py`）
2. 在真实 Stereo-seq 数据上运行验证
3. 修复集成测试中发现的问题
4. 性能优化（大数据集处理）
5. 完善错误处理边界情况

---

## 环境信息

- Python: 3.10.20 (boneage conda env)
- Scanpy: 1.11.5
- Squidpy: 1.6.5
- LangGraph: 1.2.6
- Anthropic SDK: 0.111.0
- Streamlit: 1.58.0
- LLM: deepseek/deepseek-v4-flash (via PPIO)
- GPU: N/A（CPU 模式）
- Mem: 16GB+ 建议