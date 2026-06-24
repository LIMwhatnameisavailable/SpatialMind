# SpatialMind 架构设计

## 一、系统架构总览

```
用户输入 (Streamlit UI)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              LangGraph Agent Core                   │
│                                                     │
│  START → intent_parser → planner (ThinkingBlock)    │
│                              │                      │
│                              ▼                      │
│  ┌─────────────────────────────────┐                │
│  │      executor → checker         │                │
│  │        ↑    ↓ pass    ↓ fail    │                │
│  │        │  explainer  error_handler               │
│  │        └──────────┘   loop      │                │
│  └─────────────────────────────────┘                │
│                              │ all steps done       │
│                              ▼                      │
│                       skill_invoker                 │
│                              │                      │
│                              ▼                      │
│                          END                        │
└─────────────────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
   Tools Layer    Skills Layer    Data Layer
  (Scanpy/Squidpy) (LLM增强)    (ADATA_CACHE)
```

## 二、节点设计详解

### 1. intent_parser（规则引擎，不调用 LLM）

**输入**: `user_input`（自然语言文本）

**处理逻辑**:
- 正则匹配 `.h5ad` 文件路径
- 关键词匹配分析意图（qc, preprocess, cluster 等）
- 路径关键词判断数据类型（stereo / visium）
- 若未检测到意图，使用默认全流程

**输出**: 初始化的 `AgentState`（analysis_plan, data_type, adata_cache_key 等）

### 2. planner（调用 LLM ThinkingBlock）

**输入**: intent_parser 的结果 + 用户原始输入

**处理逻辑**:
- 构建包含数据信息和用户意图的 prompt
- 调用 `call_llm_with_thinking()` 获取思考过程 + 计划
- 解析响应中的 `PLAN_STEPS` 和 `PARAMS` 行
- 若 LLM 解析失败，fallback 到 intent_parser 的结果

**亮点**: ThinkingBlock 的内容在前端 Tab3 实时展示，用户可见推理过程

### 3. executor（纯代码执行，不调用 LLM）

**输入**: `analysis_plan` 中的下一个步骤

**处理逻辑**:
- 从 `analysis_plan` 中找到第一个未完成的步骤
- 通过 `TOOL_MAP` 映射到 `tools/` 下的对应函数
- 动态 `importlib.import_module()` 加载工具
- 执行工具函数，传入 `adata_cache_key` + step_params

**工具步到函数映射**:
| 步骤 | 工具文件 | 函数 |
|------|---------|------|
| qc | tools/qc.py | run_qc |
| preprocess | tools/preprocessing.py | run_preprocessing |
| dimred | tools/dimred.py | run_dimred |
| cluster | tools/clustering.py | run_clustering |
| spatial | tools/spatial_viz.py | run_spatial_viz |
| marker | tools/marker_genes.py | run_marker_analysis |
| svg | tools/svg.py | run_svg |

### 4. checker（调用 LLM 检查）

**输入**: executor 的输出（summary + metrics + figure_paths）

**处理逻辑**:
- 若有图表生成 → 直接判定 `pass`
- 否则用 LLM 判断结果是否合理
- 返回决策: `pass` / `fail` / `skip`

**路由**:
- `pass` → explainer（生成解释）
- `fail` → error_handler（重试）
- `skip` → executor（跳过，继续下一步）

### 5. explainer（调用 LLM 解释）

**输入**: 当前步骤的结果（summary + metrics）

**输出**: 自然语言解释文字，存入 `explanations[current_step]`

**规则**: 只描述事实，不编造生物学结论

### 6. error_handler（规则引擎，不调用 LLM）

**输入**: 错误信息 + retry_count

**处理逻辑**:
- `retry_count < max_retries` → 清除当前步骤的 completed 标记 → 返回 executor
- `retry_count >= max_retries` → 跳过当前步骤 → 标记为已完成（跳过状态）

### 7. skill_invoker（调用 LLM）

**输入**: 所有步骤完成后的完整 AgentState

**处理逻辑**:
1. 调用 NaturePublishSkill（panel_composer, caption_writer, methods_writer, html_report）
2. 调用 BioInsightSkill（cluster_namer, spatial_story, qc_interpreter, insight_extractor）
3. 输出写入 `skill_outputs`

## 三、数据流

### AnnData 对象的处理

```
文件 (.h5ad)
    │
    ▼
tools.data_loader.load_data()
    │  读取并缓存到 ADATA_CACHE[adata_cache_key]
    ▼
AgentState 中保存 adata_cache_key（字符串）
    │
    ▼
各工具函数通过 adata_cache_key 从 ADATA_CACHE 获取 AnnData
    │
    ▼
工具函数就地修改 AnnData（归一化、聚类等），更新缓存
    │
    ▼
State 中只存可序列化的 summary + metrics + figure_paths
```

**关键设计**: AnnData 不序列化到 State（避免 PickleError），通过全局字典 ADATA_CACHE 中转。

### 图片生成流程

```
工具函数 → matplotlib 图 → outputs/figures/{step}_{timestamp}.png
                              │
                              ▼
                          figure_paths 存入 step_results
                              │
                              ▼
                          Streamlit Tab2 展示
```

## 四、持久化

使用 `SqliteSaver`，数据库文件 `outputs/checkpoints.db`。
通过 `session_id` (thread_id) 恢复会话。

## 五、LLM 调用架构

```
app.py / agent/nodes/
        │
        ▼
agent/llm_client.py（统一封装）
        │
        ▼
anthropic.Anthropic（SDK）
        │
        ▼
PPIO API（中转，指向 deepseek/deepseek-v4-flash）
```

所有 LLM 调用必须通过 `llm_client.py` 的 `call_llm()` 或 `call_llm_with_thinking()`。

## 六、Skills 层设计

### NaturePublishSkill

| 模块 | 功能 | 技术 |
|------|------|------|
| palette.py | 配色方案 | 预定义色板（Nature/Cell/Science） |
| panel_composer.py | 多子图排版 | PIL + matplotlib |
| caption_writer.py | 图注生成 | LLM |
| methods_writer.py | Methods 段落 | LLM |
| language_polish.py | 语言润色 | LLM |
| cover_letter.py | Cover letter | LLM |
| word_exporter.py | Word 导出 | python-docx |
| html_report.py | HTML 报告 | 模板生成 |

### BioInsightSkill

| 模块 | 功能 | 技术 |
|------|------|------|
| cluster_namer.py | Cluster 命名 | LLM + marker genes |
| spatial_story.py | 空间叙事 | LLM |
| qc_interpreter.py | QC 解读 | LLM |
| next_step.py | 下一步建议 | LLM |
| lit_reader.py | 文献阅读 | pypdf + LLM |
| insight_extractor.py | 关键发现 | LLM（带免责声明） |

## 七、错误处理策略

```
executor 异常
    │
    ▼
checker: "fail"
    │
    ▼
error_handler
    ├── retry < max_retries → executor（自动重试）
    └── retry >= max_retries → 跳过此步骤，继续下一项
```

重试不修改 `analysis_plan`，只更新 `step_params`（如调整聚类分辨率）。