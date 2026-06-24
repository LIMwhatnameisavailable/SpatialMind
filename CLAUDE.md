# CLAUDE.md — SpatialMind Agent 开发总纲

> 每次新会话开始时，必须先读本文件，再读 STEPS.md 确认当前进度，再开始工作。
> 禁止在未读完本文件的情况下直接写代码。

---

## 项目一句话定位

SpatialMind 是一个基于 LangGraph 构建的空间转录组分析 Agent，能够接收用户自然语言指令，动态规划并执行 Scanpy/Squidpy 分析流程，通过两个 Skill 模块输出发表级结果与生物学洞察，前端使用 Streamlit 展示。

---

## 目录结构（必须严格遵守）

```
SpatialMind/
├── CLAUDE.md                  # 本文件，CC开发总纲
├── STEPS.md                   # 当前开发进度（每完成一步打勾）
├── ARCHITECTURE.md            # 系统架构与节点设计详细说明
├── SKILLS.md                  # 两个Skill模块的完整规范
├── PROMPTS.md                 # 所有LLM节点的Prompt模板
├── DATA_SCHEMA.md             # 数据字段说明（obs/var/spatial）
├── README.md                  # 对外展示文档
├── .env                       # API Key（不提交git）
├── .gitignore
├── requirements.txt
│
├── app.py                     # Streamlit入口，唯一的前端文件
│
├── agent/                     # LangGraph Agent核心
│   ├── __init__.py
│   ├── graph.py               # LangGraph图定义（节点+边+编译）
│   ├── state.py               # AgentState TypedDict定义
│   ├── nodes/                 # 每个节点一个文件
│   │   ├── __init__.py
│   │   ├── intent_parser.py   # 解析用户自然语言意图
│   │   ├── planner.py         # 生成分析计划（调LLM）
│   │   ├── executor.py        # 调用tools执行单步分析
│   │   ├── checker.py         # 检查执行结果是否合理
│   │   ├── skill_invoker.py   # 调用Skills层
│   │   ├── explainer.py       # 生成结果文字解释（调LLM）
│   │   └── error_handler.py   # 错误捕获与重试决策
│   └── llm_client.py          # 统一的LLM调用封装（Anthropic SDK）
│
├── tools/                     # 纯Scanpy/Squidpy分析工具，禁止在此调用LLM
│   ├── __init__.py
│   ├── data_loader.py         # 读取h5ad，输出数据概览
│   ├── qc.py                  # QC过滤 + QC图
│   ├── preprocessing.py       # 归一化/log/HVG/scale
│   ├── dimred.py              # PCA + UMAP
│   ├── clustering.py          # Leiden/Louvain聚类
│   ├── spatial_viz.py         # 空间分布可视化
│   ├── marker_genes.py        # Marker gene分析
│   ├── svg.py                 # 空间可变基因（扩展功能）
│   └── plot_style.py          # 全局绘图样式（统一 rcParams + cluster 配色）
│
├── skills/                    # 两个Skill模块
│   ├── __init__.py
│   ├── nature_publish/        # NaturePublishSkill
│   │   ├── __init__.py
│   │   ├── palette.py         # Nature/Cell/Science配色方案
│   │   ├── panel_composer.py  # 多子图排版
│   │   ├── caption_writer.py  # 图注生成（调LLM）
│   │   ├── methods_writer.py  # Methods段落生成（调LLM）
│   │   ├── language_polish.py # 语言润色（调LLM）
│   │   ├── cover_letter.py    # Cover letter生成（调LLM）
│   │   ├── word_exporter.py   # 导出.docx论文（python-docx）
│   │   └── html_report.py     # 导出HTML报告
│   └── bio_insight/           # BioInsightSkill
│       ├── __init__.py
│       ├── cluster_namer.py   # Cluster命名（LLM + CellMarker API）
│       ├── spatial_story.py   # 空间叙事文字生成（调LLM）
│       ├── qc_interpreter.py  # QC结果解读（调LLM）
│       ├── next_step.py       # 建议下一步分析（调LLM）
│       ├── lit_reader.py      # PDF文献阅读与总结（pypdf + LLM）
│       └── insight_extractor.py # 提炼key findings（调LLM，带免责声明）
│
├── data/                      # 数据目录（不提交git，除schema）
│   └── schema/
│       ├── stereo_schema.json # Stereo-seq数据字段说明
│       └── visium_schema.json # Visium数据字段说明
│
├── outputs/                   # 所有生成的图表和报告（运行时创建）
│   ├── figures/
│   ├── reports/
│   └── exports/
│
└── tests/                     # 测试文件
    ├── test_tools.py          # Tools层单元测试（用mock数据）
    ├── test_skills.py         # Skills层测试
    └── test_graph.py          # LangGraph流程测试
```

---

## 技术栈与版本约束

使用 boneage 环境作为开发环境。
```
Python        3.10.20
scanpy        1.11.5
anndata       0.11.4
squidpy       1.6.5
langgraph     >=0.2.0
langchain     >=0.3.0
anthropic     >=0.40.0        # 用于调用PPIO中转的LLM
streamlit     >=1.40.0
python-docx   >=1.1.0
pypdf         >=4.0.0
python-dotenv >=1.0.0
matplotlib    >=3.8.0
seaborn       >=0.13.0
plotly        >=5.20.0
requests      >=2.31.0
```

安装命令：`pip install -r requirements.txt`

---

## LLM 客户端配置（唯一调用方式）

**所有LLM调用必须通过 `agent/llm_client.py` 的统一接口，禁止在其他文件直接实例化 Anthropic client。**

```python
# agent/llm_client.py 的接口规范
def get_llm_client() -> anthropic.Anthropic
def call_llm(prompt: str, system: str = "", max_tokens: int = 2048) -> str
def call_llm_with_thinking(prompt: str, system: str = "") -> tuple[str, str]
# 返回 (thinking_content, response_text)
```

配置来源：`.env` 文件
```
PPIO_BASE_URL=https://api.ppio.com/anthropic
LLM_MODEL_NAME=deepseek/deepseek-v4-flash
```

SDK使用方式：Anthropic SDK，`base_url` 指向 PPIO 端点。
模型有 ThinkingBlock，`call_llm_with_thinking` 用于 Planner 节点以展示推理过程。

---

## AgentState 定义（核心，不得随意修改字段名）

```python
# agent/state.py
from typing import TypedDict, Optional, Any
import anndata

class AgentState(TypedDict):
    # 用户输入
    user_input: str                    # 原始自然语言输入
    session_id: str                    # 会话ID，用于SqliteSaver

    # 数据状态
    data_path: str                     # h5ad文件路径
    data_type: str                     # "stereo" | "visium" | "unknown"
    adata_cache_key: str               # adata在内存缓存中的key

    # 分析计划
    analysis_plan: list[str]           # 规划的步骤列表，如["qc","preprocess","cluster"]
    current_step: str                  # 当前执行的步骤名
    completed_steps: list[str]         # 已完成的步骤
    step_params: dict[str, Any]        # 每个步骤的参数，如{"leiden_resolution": 0.5}

    # 结果存储
    figures: dict[str, str]            # 步骤名 -> 图片文件路径
    step_results: dict[str, Any]       # 步骤名 -> 结果摘要（可序列化）
    explanations: dict[str, str]       # 步骤名 -> LLM生成的解释文字

    # Skills输出
    skill_outputs: dict[str, Any]      # skill名 -> 输出内容

    # 错误与控制
    error_message: Optional[str]       # 当前错误信息
    retry_count: int                   # 当前步骤重试次数
    max_retries: int                   # 最大重试次数（默认2）
    is_complete: bool                  # 整体流程是否完成

    # LLM对话历史
    messages: list[dict]               # 用于多轮对话的消息历史
```

**注意**：AnnData 对象本身不存入 State（无法序列化），使用全局内存缓存 `tools/data_loader.py` 中的 `ADATA_CACHE: dict[str, AnnData]`，通过 `adata_cache_key` 访问。

---

## LangGraph 图结构（graph.py 实现规范）

### 节点列表与职责

| 节点名 | 文件 | 是否调用LLM | 职责 |
|--------|------|------------|------|
| `intent_parser` | nodes/intent_parser.py | ✅ | 解析用户输入，提取数据路径、分析意图、参数偏好 |
| `planner` | nodes/planner.py | ✅ ThinkingBlock | 生成有序分析步骤列表，写入 analysis_plan |
| `executor` | nodes/executor.py | ❌ | 从 analysis_plan 取下一步，调用对应 tool |
| `checker` | nodes/checker.py | ✅ | 检查 tool 输出是否合理，决定 pass/retry/skip |
| `skill_invoker` | nodes/skill_invoker.py | ✅ | 在分析完成后调用 Skills 层 |
| `explainer` | nodes/explainer.py | ✅ | 为每步结果生成简短解释（不编造生物学结论） |
| `error_handler` | nodes/error_handler.py | ❌ | 记录错误，决定重试或跳过 |

### 边与条件路由

```
START → intent_parser → planner → executor
executor → checker
checker → explainer          (条件: result == "pass")
checker → error_handler      (条件: result == "fail" and retry_count < max_retries)
checker → executor           (条件: result == "skip")
error_handler → executor     (条件: retry_count < max_retries，更新参数重试)
error_handler → planner      (条件: retry_count >= max_retries，重新规划)
explainer → executor         (条件: 还有未完成步骤)
explainer → skill_invoker    (条件: 所有步骤完成)
skill_invoker → END
```

### 持久化配置

使用 `langgraph.checkpoint.sqlite.SqliteSaver`，数据库文件存放于 `outputs/checkpoints.db`。
每次调用 `graph.invoke()` 时传入 `config={"configurable": {"thread_id": session_id}}`。

---

## Tools 层开发规范

**核心约束：Tools 层禁止调用 LLM，只允许使用 Scanpy/Squidpy/matplotlib。**

每个 tool 函数签名规范：
```python
def tool_name(adata_key: str, **params) -> dict:
    """
    Args:
        adata_key: ADATA_CACHE中的key
        **params: 分析参数
    Returns:
        {
            "status": "success" | "error",
            "summary": str,          # 可序列化的文字摘要
            "figure_paths": list[str], # 生成的图片路径列表
            "metrics": dict,         # 关键数值指标
            "error": str | None
        }
    """
```

图片统一保存到 `outputs/figures/{step_name}_{timestamp}.png`，DPI=150。

---

## Skills 层开发规范

详见 SKILLS.md。Skills 可以调用 LLM，但必须：
1. 在输出中标注"AI生成内容，仅供参考"
2. 不编造具体数值（只能引用 step_results 中的真实数据）
3. 每个 Skill 函数接收 `AgentState` 作为输入，返回更新后的 `skill_outputs`

---

## Streamlit 前端规范（app.py）

页面结构：
```
侧边栏：文件上传 | 数据类型选择 | 分析参数设置 | Skills开关
主区域：
  Tab1: 💬 分析对话（用户输入 + Agent回复流）
  Tab2: 📊 分析结果（图表展示，按步骤组织）
  Tab3: 🧠 Agent思考（LangGraph节点执行路径可视化）
  Tab4: 📄 导出中心（下载报告/Word/HTML）
```

Tab3"Agent思考"是展示 LangGraph 执行过程的关键，需要实时显示当前节点名和 Planner 的 ThinkingBlock 内容。

---

## 禁止事项

1. ❌ 禁止在 `tools/` 目录下的任何文件中调用 LLM
2. ❌ 禁止在 `agent/nodes/` 以外的地方直接实例化 Anthropic client
3. ❌ 禁止修改 AgentState 的字段名（只能新增）
4. ❌ 禁止将 AnnData 对象存入 State
5. ❌ 禁止在 Skills 输出中编造未经数据支持的生物学结论
6. ❌ 禁止提交 `.env` 文件到 git
7. ❌ 禁止在任何 tools/ 或 skills/ 的绘图函数中使用 matplotlib 默认样式，必须在函数开头调用 apply_global_style()
8. ❌ 禁止对同一 adata 对象多次调用 clustering 工具（会导致 cluster 列被覆盖，图表内容重复）
9. ❌ 禁止在 LangGraph 节点函数中使用 print() 调试，改用 state["error_message"] 或 logging
10. ❌ 禁止在未完成 Phase 9.1 最小闭环测试的情况下修改 Streamlit 前端

---

## 参考文档索引

- 当前进度：`STEPS.md`
- 架构细节：`ARCHITECTURE.md`
- Skills规范：`SKILLS.md`
- Prompt模板：`PROMPTS.md`
- 绘图规范：`PLOT_GUIDE.md`
- 数据字段：`DATA_SCHEMA.md`
