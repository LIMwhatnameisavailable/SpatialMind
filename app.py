"""
SpatialMind Streamlit 前端入口 — Phase 9.4

页面结构（5 Tab）：
  Tab 1: 分析（主界面）— 侧边栏输入 + 对话 + 图表 + BioInsight
  Tab 2: 图表库           — 浏览 outputs/figures/ 下所有 PNG，按步骤分组
  Tab 3: Agent 思考       — 节点执行路径 / Planner 推理 / 分析计划 / 步骤详情
  Tab 4: 报告             — NaturePublish Skill 输出（Methods / 图注 / 摘要）+ 复制按钮
  Tab 5: 日志             — completed_steps / 错误 / 完整 state JSON
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

# ── 页面配置（必须在第一行） ──
st.set_page_config(
    page_title="SpatialMind — 空间转录组分析 Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 自定义 CSS（GitHub Dark 科技风） ──
st.markdown("""
<style>
/* ════════════════════════════════════════════
   GitHub Dark 主题配色
   背景: #0d1117  | 侧边栏: #161b22
   卡片: #21262d  | 边框: #30363d
   强调: #58a6ff(蓝) + #3fb950(绿)
   错误红: #f85149 | 警告黄: #d29922
   ════════════════════════════════════════════ */

/* ── 全局背景 + 去除顶部空白 ── */
.stApp { background-color: #0d1117; }
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100%;
}
section.main > div:first-child {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* ── 侧边栏: 全高对齐 + 隐藏溢出 ── */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    height: 100vh !important;
    overflow: hidden !important;
}
[data-testid="stSidebarContent"] {
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}
[data-testid="stSidebar"] .stMarkdown { color: #c9d1d9; }

/* ── 主内容 ── */
[data-testid="stVerticalBlock"] > div {
    background-color: transparent;
}

/* ── Tab 栏: 激活明显高亮 ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #161b22;
    border-radius: 8px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #30363d;
}
.stTabs [data-baseweb="tab"] {
    color: #8b949e;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    transition: all 0.2s ease;
    border-bottom: none !important;
}
.stTabs [aria-selected="true"] {
    background-color: #1f6feb33 !important;
    color: #58a6ff !important;
    font-weight: 600 !important;
    border-bottom: none !important;
    box-shadow: inset 0 -2px 0 #58a6ff !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #e6edf3;
    background-color: #21262d66;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1rem;
}

/* ── 按钮 ── */
.stButton > button {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid rgba(46, 160, 67, 0.4);
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}
.stButton > button[kind="primary"] {
    background-color: #1f6feb;
    border-color: rgba(56, 139, 253, 0.4);
    color: #ffffff;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background-color: #388bfd;
    border-color: #58a6ff;
}

/* ── 输入框 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #58a6ff;
    box-shadow: 0 0 0 1px #58a6ff;
}

/* ── 选择框 ── */
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] {
    background-color: #0d1117;
    border-color: #30363d;
}

/* ── 消息样式 ── */
.stSuccess {
    border-left: 3px solid #3fb950;
    background-color: #3fb95012;
    color: #7ee787;
}
.stError {
    border-left: 3px solid #f85149;
    background-color: #f8514912;
    color: #ff7b72;
}
.stInfo {
    border-left: 3px solid #58a6ff;
    background-color: #58a6ff12;
    color: #79c0ff;
}
.stWarning {
    border-left: 3px solid #d29922;
    background-color: #d2992212;
    color: #e3b341;
}

/* ── 进度条 ── */
.stProgress > div > div > div { background-color: #2ea043; }

/* ── 通用文字: 系统字体栈 ── */
.stMarkdown, p, span, label {
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
h1, h2, h3 {
    color: #e6edf3 !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}
h1 { font-size: 1.6rem; border-bottom: 1px solid #21262d; padding-bottom: 0.3rem; }
h2 { font-size: 1.3rem; }
h3 { font-size: 1.1rem; }

/* ── 图片容器 ── */
[data-testid="stImage"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #30363d;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}
[data-testid="stExpander"] summary {
    font-weight: 500;
    color: #e6edf3;
}

/* ── 分隔线 ── */
hr { border-color: #30363d !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 12px;
}
[data-testid="stMetricLabel"] { color: #8b949e; }
[data-testid="stMetricValue"] { color: #e6edf3; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 8px;
}
[data-testid="stDataFrame"] table {
    background-color: #0d1117;
}

/* ── Code block ── */
.stCodeBlock {
    background-color: #161b22 !important;
    border: 1px solid #30363d;
    border-radius: 8px;
}

/* ── 文件上传器 ── */
[data-testid="stFileUploader"] {
    background-color: #0d1117;
    border: 1px dashed #30363d;
    border-radius: 8px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #58a6ff;
}

/* ── 侧边栏卡片 & Step 卡片 ── */
.step-card {
    background-color: #21262d !important;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    border: 1px solid #30363d;
}

/* ── 侧边栏标题 ── */
.sidebar-section-header {
    color: #58a6ff !important;
    font-weight: 600 !important;
    font-size: 0.9em;
    margin-bottom: 4px;
}

/* ── 开关/勾选框 ── */
[data-testid="stCheckbox"] label span { color: #c9d1d9; }
[data-testid="stBaseButton-toggle"] {
    background-color: #30363d;
}

/* ── Caption ── */
.stCaption, .caption {
    color: #8b949e;
    font-size: 0.8em;
}

/* ── Status ── */
[data-testid="stStatusWidget"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}

/* ════════════════════════════════════════════
   隐藏顶部白条 — 以下选择器消除 Streamlit
   默认的白色 header / toolbar / decoration /
   hamburger menu / footer，使深色背景无缝。
   ════════════════════════════════════════════ */
[data-testid="stHeader"] {
    background: #0d1117 !important;
    height: 0.1rem !important;
    border-bottom: none !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}
[data-testid="stDecoration"] {
    display: none !important;
}
#MainMenu {
    visibility: hidden !important;
}
footer {
    visibility: hidden !important;
}
/* 在隐藏 header 后给主内容区补回合理的顶部间距，避免内容贴顶 */
.main .block-container {
    padding-top: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── 路径 ──
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

# ── 加载 Streamlit Cloud Secrets ──
# 本地开发使用 .env 文件；云端部署在 Streamlit Dashboard → Settings → Secrets 中设置
# 需要的 secrets: PPIO_API_KEY, PPIO_BASE_URL, LLM_MODEL_NAME
try:
    for key in ["PPIO_API_KEY", "PPIO_BASE_URL", "LLM_MODEL_NAME"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass  # 本地开发时 st.secrets 可能不存在

from agent.graph import app as langgraph_app
from agent.state import get_initial_state
from tools.plot_style import (
    get_figure_meta,
    get_step_display_name,
    manage_session_figures,
    discover_session_figures,
)

# ── 初始化 Session State ──
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "data_info" not in st.session_state:
    st.session_state.data_info = {}
if "analysis_start_time" not in st.session_state:
    st.session_state.analysis_start_time = None
if "output_dir" not in st.session_state:
    st.session_state.output_dir = "outputs/figures"
if "available_runs" not in st.session_state:
    st.session_state.available_runs = []  # [{session_id, run_timestamp, path, n_figures, mtime_dt}, ...]
if "selected_run" not in st.session_state:
    st.session_state.selected_run = None  # 当前选中的 run path


# ══════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════

def get_session_run_path(session_id: str) -> str:
    """
    获取 session 的最新 run 目录，若不存在则创建。
    """
    base = Path(FIGURES_DIR) / session_id
    base.mkdir(parents=True, exist_ok=True)
    # 按目录名排序取最新
    if base.exists():
        runs = sorted([d.name for d in base.iterdir() if d.is_dir()], reverse=True)
        if runs:
            return str(base / runs[0])
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)
    return str(run_dir)


def get_step_name_from_filename(filename: str) -> str:
    """从图片文件名推断步骤名"""
    from tools.plot_style import _infer_step_from_filename
    return _infer_step_from_filename(filename)


def _list_available_runs(session_id: str = None) -> list[dict]:
    """
    扫描 outputs/figures/，列出指定 session 下的所有 run 目录（按时间倒序）。

    Args:
        session_id: 若传入，只返回该 session 的 run；否则返回所有 session 的最新 run

    Returns:
        按 run 目录 mtime 倒序的列表
    """
    runs = []
    base = Path(FIGURES_DIR)
    if not base.exists():
        return runs

    # 遍历 session 目录
    for session_dir in sorted(base.iterdir(), reverse=True):
        if not session_dir.is_dir():
            continue
        if session_id and session_dir.name != session_id:
            continue

        # 遍历 run 目录（按名字倒序 = 最新在前）
        for run_dir in sorted(session_dir.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
            n_png = len(list(run_dir.glob("*.png")))
            runs.append({
                "session_id": session_dir.name,
                "run_timestamp": run_dir.name,
                "path": str(run_dir),
                "n_figures": n_png,
                "mtime_dt": datetime.fromtimestamp(run_dir.stat().st_mtime),
            })
            # 如果指定了 session，只取该 session 下所有 run；否则每个 session 只取最新一个
            if not session_id:
                break

    # 按 mtime 倒序
    runs.sort(key=lambda r: r["mtime_dt"], reverse=True)
    return runs


def _find_latest_run_dir() -> str | None:
    """
    降级处理：扫描 outputs/figures/ 下所有子目录，取图片最多的最新 run 目录。

    Returns:
        目录路径，或 None
    """
    all_runs = _list_available_runs(session_id=None)  # 每个 session 最新一条
    if not all_runs:
        return None
    # 取图片最多的
    all_runs.sort(key=lambda r: r["n_figures"], reverse=True)
    return all_runs[0]["path"] if all_runs else None


# ══════════════════════════════════════════
# 统一渲染函数
# ══════════════════════════════════════════

def render_agent_response(final_state: dict) -> bool:
    """
    统一渲染函数：QA / no_data 直接显示文字回答，analysis 返回 False。
    返回 True 表示已处理（不再显示分析步骤）。
    """
    request_type = final_state.get("request_type", "")
    messages = final_state.get("messages", [])
    is_complete = final_state.get("is_complete", False)
    analysis_plan = final_state.get("analysis_plan", [])

    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    last_answer = assistant_msgs[-1].get("content", "") if assistant_msgs else ""

    if request_type in ("qa", "no_data", "result_explanation") or (
        is_complete and not analysis_plan
    ):
        st.divider()
        if last_answer:
            st.markdown("### 🤖 Agent 回答")
            with st.container():
                st.markdown(last_answer)
        else:
            st.warning(
                final_state.get("error_message")
                or "Agent 已完成，但没有生成可显示的回答。"
            )
        return True

    return False


# ══════════════════════════════════════════
# 侧边栏
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2em;'>🧬</div>
        <div style='font-size:1.3em; font-weight:700; color:#58a6ff;'>SpatialMind</div>
        <div style='font-size:0.75em; color:#8b949e; margin-top:4px;'>空间转录组智能分析平台</div>
    </div>
    <hr style='border-color:#30363d; margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.divider()

    # ── 数据输入 ──
    st.markdown('<p class="sidebar-section-header">📁 数据输入</p>', unsafe_allow_html=True)

    data_path = st.text_input(
        "数据路径（.h5ad）",
        placeholder="data/data/anndata/visium_hne_adata.h5ad",
        help="输入 h5ad 文件路径，或上传文件",
    )

    uploaded_file = st.file_uploader(
        "或上传 .h5ad 文件", type=["h5ad"]
    )
    if uploaded_file is not None:
        os.makedirs("data/uploads", exist_ok=True)
        save_path = f"data/uploads/{uploaded_file.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        data_path = save_path
        st.success(f"已保存: {uploaded_file.name}")

    data_type = st.selectbox(
        "数据类型",
        options=["auto", "visium", "stereo", "unknown"],
        index=0,
        help="auto 自动检测; visium: 10x Visium; stereo: Stereo-seq",
    )

    if st.button("📥 验证路径", use_container_width=True):
        if not data_path:
            st.warning("请输入或上传文件路径。")
        elif os.path.exists(data_path):
            st.session_state.data_loaded = True
            fsize_mb = os.path.getsize(data_path) / (1024 * 1024)
            st.session_state.data_info = {
                "n_obs": "—（分析后显示）",
                "n_vars": "—（分析后显示）",
                "file_size_mb": f"{fsize_mb:.1f}",
            }
            st.success(f"✅ 文件存在: {Path(data_path).name} ({fsize_mb:.1f} MB)")
        else:
            st.error(f"文件不存在: {data_path}")
            st.session_state.data_loaded = False

    st.divider()

    # ── 分析参数 ──
    st.markdown('<p class="sidebar-section-header">⚙️ 分析参数</p>', unsafe_allow_html=True)

    clustering_resolution = st.slider(
        "聚类分辨率", 0.1, 2.0, 0.5, 0.1
    )
    n_pcs = st.slider("PCA 主成分数", 10, 100, 50, 5)
    n_top_genes = st.slider("Top HVG 数量", 500, 5000, 2000, 100)

    st.divider()

    # ── Skills 设置 ──
    st.markdown("### 🎨 Skills 设置")
    enable_nature_publish = st.toggle("🎨 NaturePublish 模式", value=True, key="toggle_nature")
    enable_bio_insight = st.toggle("🧠 BioInsight 洞察", value=True, key="toggle_bio")

    st.divider()
    st.caption(f"会话 `{st.session_state.session_id[:8]}...`")
    if st.session_state.data_loaded:
        st.success("✅ 数据已加载")
    else:
        st.info("⏳ 数据未加载")

    # 当前图表目录状态
    current_dir = st.session_state.output_dir
    if current_dir and current_dir != "outputs/figures":
        rel = os.path.relpath(current_dir, str(FIGURES_DIR))
        st.caption(f"📁 图表: `{rel}`")


# ══════════════════════════════════════════
# 主区域 — 5 个 Tab
# ══════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔬 分析",
    "🖼️ 图表库",
    "🧠 Agent思考",
    "📄 报告",
    "📋 日志",
])


# ══════════════════════════════════════════
# Tab 1 · 分析（主界面）
# ══════════════════════════════════════════
with tab1:
    st.header("🔬 空间转录组分析")
    st.caption("输入自然语言描述，Agent 自动规划并执行分析流程。")

    # ── 上方：聊天输入区 ──
    st.subheader("💬 分析需求")
    prompt = st.text_area(
        "描述分析需求：",
        value="请读取数据并执行完整分析流程（QC → 预处理 → 降维 → 聚类 → 空间可视化 → Marker 基因），最后给出生物学解读。",
        height=80,
        label_visibility="collapsed",
    )

    col_run, col_status = st.columns([1, 3])
    with col_run:
        run_clicked = st.button("🚀 发送给 Agent", type="primary", use_container_width=True)
    with col_status:
        if st.session_state.data_loaded:
            info = st.session_state.data_info
            st.caption(
                f"数据已加载: {info.get('n_obs', '?')} 细胞 × {info.get('n_vars', '?')} 基因"
            )

    # ── 分析执行 ──
    if run_clicked:
        # 保存用户输入
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 自动加载数据（如果尚未加载）——仅校验文件存在，具体加载由 graph.invoke 负责
        if not st.session_state.data_loaded and data_path:
            if os.path.exists(data_path):
                st.session_state.data_loaded = True
                st.session_state.data_info = {
                    "n_obs": "—（分析后显示）",
                    "n_vars": "—（分析后显示）",
                    "file_size_mb": f"{os.path.getsize(data_path) / (1024 * 1024):.1f}",
                }
            else:
                st.error(f"数据文件不存在: {data_path}")
                st.stop()

        # 构建初始 state
        session_id = st.session_state.session_id

        # 创建 session 子目录并清理旧 session
        run_dir = manage_session_figures(session_id, keep_n=2)
        st.session_state.output_dir = run_dir
        st.session_state.available_runs = _list_available_runs(session_id=session_id)
        st.session_state.selected_run = run_dir

        step_params = {
            "cluster": {"resolution": clustering_resolution},
            "dimred": {"n_pcs": n_pcs, "n_neighbors": 15},
            "preprocess": {"n_top_genes": n_top_genes},
            "enable_nature_publish": enable_nature_publish,
            "enable_bio_insight": enable_bio_insight,
        }
        initial_state = get_initial_state(
            user_input=prompt,
            data_path=data_path or "",
            data_type=data_type if data_type != "auto" else "unknown",
            step_params=step_params,
            session_id=st.session_state.session_id,
            output_dir=run_dir,
        )

        st.session_state.analysis_start_time = datetime.now()

        # 执行 Agent
        with st.status("🧠 Agent 分析中...", expanded=True) as status:
            try:
                result = langgraph_app.invoke(
                    initial_state,
                    config={"configurable": {"thread_id": st.session_state.session_id}},
                )
                st.session_state.agent_state = result
                st.session_state.analysis_done = True
                status.update(label="✅ 分析完成!", state="complete")
            except Exception as e:
                status.update(label="❌ 分析失败", state="error")
                st.error(f"Agent 执行出错: {e}")
                st.exception(e)

        st.rerun()

    # ── 分析完成后：展示结果 ──
    if st.session_state.analysis_done and st.session_state.agent_state:
        agent_state = st.session_state.agent_state

        # 先尝试统一渲染（QA / no_data 直接显示文字回答）
        handled = render_agent_response(agent_state)

        # 只有 analysis 请求才渲染分析流程
        if not handled:
            # analysis 结果渲染
            completed = agent_state.get("completed_steps", [])
            plan = agent_state.get("analysis_plan", [])
            figures = agent_state.get("figures", {})
            step_results = agent_state.get("step_results", {})
            explanations = agent_state.get("explanations", {})
            skill_outputs = agent_state.get("skill_outputs", {})

            st.divider()
            st.success(f"✅ 分析完成！共完成 {len(completed)} 个步骤: {', '.join(completed)}")

            # ── 中部：每步结果（卡片式布局） ──
            if plan:
                for idx, step in enumerate(plan):
                    st.markdown(f'<div class="step-card">', unsafe_allow_html=True)

                    st.subheader(f"📊 Step {idx+1}: {step.upper()}")

                    # 全宽展示该步骤的所有独立图
                    if step in step_results:
                        all_figs = step_results[step].get("figure_paths", [])
                        all_figs = [f for f in all_figs if os.path.exists(f)]

                        if all_figs:
                            for fig_path in all_figs:
                                # 获取图表元数据
                                fname = os.path.basename(fig_path)
                                chart_type, description = get_figure_meta(fname)
                                type_icons = {
                                    "小提琴图": "🎻", "散点图": "🔵", "柱状图": "📊",
                                    "折线图": "📈", "UMAP图": "🌀", "条形图": "📊",
                                }
                                icon = type_icons.get(chart_type, "🖼️")
                                caption = f"{icon} {chart_type}"
                                if description:
                                    caption += f" — {description}"
                                st.image(fig_path, caption=caption, use_container_width=True)
                        else:
                            # 没有图片时，展示指标
                            metrics = step_results[step].get("metrics", {})
                            if metrics:
                                st.markdown("**📈 关键指标**")
                                st.json(metrics)
                    else:
                        st.info("暂无结果。")

                    # 解释文字 — 始终在图片下方
                    if step in explanations:
                        st.markdown("---")
                        st.markdown(f"**📝 生物学解释**")
                        st.markdown(explanations[step])
                    else:
                        st.info("暂无解释。")

                    st.markdown('</div>', unsafe_allow_html=True)

            # ── 下方：BioInsight 输出 ──
            st.divider()
            st.subheader("🧠 生物学洞察（BioInsightSkill）")

            bio = skill_outputs.get("bio_insight", {})
            if bio:
                col1, col2 = st.columns(2)
                with col1:
                    if bio.get("spatial_story"):
                        st.markdown("**空间叙事：**")
                        st.info(bio["spatial_story"])
                    if bio.get("qc_interpretation"):
                        with st.expander("QC 解读"):
                            st.markdown(bio["qc_interpretation"])

                with col2:
                    if bio.get("cluster_names"):
                        st.markdown("**Cluster 命名：**")
                        names = bio["cluster_names"]
                        if isinstance(names, dict):
                            st.json(names)
                        else:
                            st.markdown(str(names))
                    if bio.get("insights"):
                        with st.expander("关键发现"):
                            st.markdown(bio["insights"])

                if bio.get("disclaimer"):
                    st.caption(bio["disclaimer"])
            else:
                st.info("BioInsightSkill 未启用或未生成输出。")

            # NaturePublish 快速预览
            nature = skill_outputs.get("nature_publish", {})
            if nature:
                st.divider()
                st.subheader("📄 NaturePublishSkill 预览")
                if nature.get("methods"):
                    st.markdown(
                        f'<div class="step-card">'
                        f'<h4>📝 Methods 段落</h4>'
                        f'{nature["methods"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                if nature.get("captions"):
                    st.markdown(
                        f'<div class="step-card">'
                        f'<h4>🏷️ 图注（Figure Captions）</h4>'
                        f'{nature["captions"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    elif not st.session_state.analysis_done:
        st.info("👆 输入分析需求后点击「开始分析」。")


# ══════════════════════════════════════════
# Tab 2 · 图表库（支持 Session 切换 + 降级回退）
# ══════════════════════════════════════════
with tab2:
    st.header("🖼️ 图表库")
    st.caption("浏览已生成的图表，按 Session 和 Run 分组。")

    # ── Session / Run 选择器 ──
    available_runs = st.session_state.available_runs
    if not available_runs:
        sid = st.session_state.session_id
        # 优先用当前 session，降级到全部扫描
        available_runs = _list_available_runs(session_id=sid)
        if not available_runs:
            available_runs = _list_available_runs(session_id=None)
        st.session_state.available_runs = available_runs

    # 降级：如果 selected_run 为空但 dir 有数据，取最新的
    selected = st.session_state.selected_run
    if not selected and available_runs:
        selected = available_runs[0]["path"]
        st.session_state.selected_run = selected

    if available_runs:
        # 构建选项标签：标记"当前分析"和"上次分析"
        current_dir = st.session_state.output_dir
        run_options = {}
        for i, r in enumerate(available_runs):
            label_parts = [f"{r['session_id'][:8]}.../{r['run_timestamp']}"]
            if r["path"] == current_dir:
                label_parts.append("← 当前")
            elif i == 0:
                label_parts.append("(最新)")
            label_parts.append(f"{r['n_figures']} figs")
            run_options[" · ".join(label_parts)] = r["path"]

        default_label = None
        if selected:
            for label, path in run_options.items():
                if path == selected:
                    default_label = label
                    break
        if default_label is None:
            default_label = list(run_options.keys())[0]

        selected_label = st.selectbox(
            "选择分析运行：",
            options=list(run_options.keys()),
            index=list(run_options.keys()).index(default_label),
            key="run_selector",
        )
        selected_run_path = run_options[selected_label]
        st.session_state.selected_run = selected_run_path

        # 刷新按钮（重新扫描当前 session）
        if st.button("🔄 刷新图表列表", use_container_width=True):
            st.session_state.available_runs = _list_available_runs(session_id=st.session_state.session_id)
            st.rerun()

        # 扫描当前选中目录
        fig_groups: dict[str, list[dict]] = {}
        for root, _dirs, files in os.walk(selected_run_path):
            for fname in sorted(files):
                if not fname.endswith(".png"):
                    continue
                fpath = os.path.join(root, fname)
                mtime_dt = datetime.fromtimestamp(os.path.getmtime(fpath))
                step = get_step_name_from_filename(fname)
                fig_groups.setdefault(step, []).append({
                    "path": fpath,
                    "filename": fname,
                    "mtime": mtime_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "mtime_dt": mtime_dt,
                })

        st.caption(f"📁 {selected_run_path}  ·  {sum(len(v) for v in fig_groups.values())} 张图")

        # 按步骤分组展示
        step_order = ["qc", "preprocess", "dimred", "cluster", "spatial", "marker", "svg"]

        for step in step_order:
            if step not in fig_groups:
                continue
            images = fig_groups[step]
            display_name = get_step_display_name(step)

            latest_mtime = max(img["mtime_dt"] for img in images)
            time_str = latest_mtime.strftime("%Y-%m-%d %H:%M")

            with st.expander(f"{display_name} · {len(images)}张图 · {time_str}", expanded=True):
                for i, img in enumerate(images):
                    chart_type, description = get_figure_meta(img["filename"])

                    st.image(img["path"], use_container_width=True)

                    type_icons = {
                        "小提琴图": "🎻", "散点图": "🔵", "柱状图": "📊",
                        "折线图": "📈", "UMAP图": "🌀", "条形图": "📊",
                    }
                    icon = type_icons.get(chart_type, "🖼️")

                    st.markdown(
                        f"<div style='margin-top:4px;'>"
                        f"<span style='background:#1e2130; padding:2px 10px; border-radius:12px; "
                        f"font-size:0.85em; color:#00d4aa; border:1px solid #00d4aa44;'>{icon} {chart_type}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    if description:
                        st.markdown(
                            f"<div style='color:#8892a4; font-style:italic; font-size:0.9em; margin:2px 0 6px 0;'>{description}</div>",
                            unsafe_allow_html=True,
                        )

                    col_meta, col_dl = st.columns([3, 1])
                    with col_meta:
                        st.caption(f"📄 {img['filename']}  🕒 {img['mtime']}")
                    with col_dl:
                        safe_key = selected_run_path.replace("/", "_").replace("\\", "_")
                        with open(img["path"], "rb") as fh:
                            st.download_button(
                                label="⬇️ 下载",
                                data=fh,
                                file_name=img["filename"],
                                mime="image/png",
                                key=f"dl_{step}_{i}_{safe_key}",
                                use_container_width=True,
                            )

                    if i < len(images) - 1:
                        st.divider()
    else:
        st.info("暂无图表。执行一次分析后会自动生成。")


# ══════════════════════════════════════════
# Tab 3 · Agent 思考
# ══════════════════════════════════════════
with tab3:
    st.header("🧠 Agent 思考")
    st.caption("LangGraph 节点执行路径与 Planner 推理过程的可视化。")

    last_state = st.session_state.get("agent_state", None)

    if last_state is None:
        st.info("请先在「🔬 分析」Tab 运行分析")
    else:
        # ── 节点执行路径 ──
        st.subheader("🔄 节点执行路径")
        NODE_SEQUENCE = ["intent_parser", "planner", "executor", "checker", "explainer", "skill_invoker"]
        completed_steps = last_state.get("completed_steps", [])
        is_complete = last_state.get("is_complete", False)

        nodes_display = []
        for node in NODE_SEQUENCE:
            if is_complete or node in completed_steps:
                icon = "✅"
            elif node == "executor" and completed_steps:
                # 如果至少有一节点完成但 executor 不在其中，说明它在执行
                icon = "🔄"
            else:
                icon = "⭕"
            label = node.replace("_", " ").title()
            nodes_display.append(f"{icon} {label}")

        # 横向排列
        col_headers = st.columns(len(NODE_SEQUENCE))
        for i, (col, display) in enumerate(zip(col_headers, nodes_display)):
            with col:
                st.markdown(
                    f"<div style='text-align:center; padding:8px 4px; "
                    f"background:#1e2130; border-radius:6px; border:1px solid #2d3250;'>"
                    f"<span style='font-size:1.1rem;'>{display}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        # 箭头连接（在节点下方）
        arrow_cols = st.columns(len(NODE_SEQUENCE) * 2 - 1)
        for i in range(len(NODE_SEQUENCE) - 1):
            arrow_cols[i * 2 + 1].markdown(
                "<div style='text-align:center; color:#58a6ff; font-size:1.5rem;'>→</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Planner 思考过程 ──
        st.subheader("🧠 Planner 推理过程")
        thinking = last_state.get("step_results", {}).get("planner_thinking", "")
        with st.expander("查看 Planner 推理过程", expanded=False):
            if thinking:
                st.markdown(thinking)
            else:
                st.info("暂无思考记录，请先运行分析")

        st.divider()

        # ── 分析计划 ──
        st.subheader("📋 分析计划")
        analysis_plan = last_state.get("analysis_plan", [])
        if analysis_plan:
            for idx, step in enumerate(analysis_plan):
                if step in completed_steps:
                    icon = "✅"
                elif step == last_state.get("current_step", ""):
                    icon = "🔄"
                else:
                    icon = "⭕"
                st.markdown(f"{icon} **{idx+1}. {step}**")
        else:
            st.info("暂无分析计划")

        st.divider()

        # ── 步骤详情 ──
        st.subheader("📌 步骤详情")
        step_results = last_state.get("step_results", {})
        explanations = last_state.get("explanations", {})
        if completed_steps:
            for step in completed_steps:
                with st.expander(f"✅ {step.upper()} 详情", expanded=False):
                    if step in step_results:
                        summary = step_results[step].get("summary", "")
                        if summary:
                            st.markdown(f"**摘要：** {summary}")
                    if step in explanations:
                        st.markdown(f"**解释：** {explanations[step]}")
        else:
            st.info("暂无已完成的步骤")


# ══════════════════════════════════════════
# Tab 4 · 报告
# ══════════════════════════════════════════
with tab4:
    st.header("📄 分析报告")
    st.caption("NaturePublishSkill 输出的发表级报告内容（AI 生成，仅供参考）。")

    if not st.session_state.analysis_done or not st.session_state.agent_state:
        st.info("请先在「分析」Tab 中执行一次完整分析。")
    else:
        agent_state = st.session_state.agent_state
        skill_outputs = agent_state.get("skill_outputs", {})
        nature = skill_outputs.get("nature_publish", {})

        if not nature:
            st.warning("NaturePublishSkill 未启用或未生成输出。请在侧边栏开启后重新分析。")
        else:
            # ── Methods 段落 ──
            methods = nature.get("methods", "")
            if methods:
                st.subheader("📝 Methods 段落")
                st.code(methods, language="markdown")
                st.button(
                    "📋 复制 Methods",
                    on_click=lambda: st.write("已复制（请手动 Ctrl+C 从上方代码框复制）"),
                    key="copy_methods",
                    use_container_width=True,
                )

            st.divider()

            # ── 图注 ──
            captions = nature.get("captions", "")
            if captions:
                st.subheader("🏷️ 图注（Figure Captions）")
                st.code(captions, language="markdown")
                st.button(
                    "📋 复制图注",
                    on_click=lambda: st.write("已复制（请手动 Ctrl+C 从上方代码框复制）"),
                    key="copy_captions",
                    use_container_width=True,
                )

            st.divider()

            # ── 润色后的摘要 ──
            polished = nature.get("polished_abstract", "")
            if polished:
                st.subheader("✨ 润色后的摘要")
                st.code(polished, language="markdown")
                st.button(
                    "📋 复制摘要",
                    on_click=lambda: st.write("已复制（请手动 Ctrl+C 从上方代码框复制）"),
                    key="copy_abstract",
                    use_container_width=True,
                )

            # ── Cover Letter ──
            cover = nature.get("cover_letter", "")
            if cover:
                st.divider()
                st.subheader("✉️ Cover Letter")
                with st.expander("查看 Cover Letter"):
                    st.markdown(cover)

            # ── 下载区域 ──
            st.markdown("---")
            st.subheader("📥 导出报告")

            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                html_path = nature.get("html_report", "")
                if html_path and os.path.exists(html_path):
                    with open(html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    st.download_button(
                        label="📥 下载 HTML 报告",
                        data=html_content,
                        file_name="SpatialMind_Report.html",
                        mime="text/html",
                        use_container_width=True,
                    )
                else:
                    st.info("请先完成分析并启用 NaturePublish 模式")

            with col_dl2:
                docx_path = nature.get("docx_path", "")
                if docx_path and os.path.exists(docx_path):
                    with open(docx_path, "rb") as f:
                        docx_content = f.read()
                    st.download_button(
                        label="📥 下载 Word 文档",
                        data=docx_content,
                        file_name="SpatialMind_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                else:
                    st.info("请先完成分析并启用 NaturePublish 模式")

            # ══════════════════════════════════════════
# Tab 5 · 日志
# ══════════════════════════════════════════
with tab5:
    st.header("📋 执行日志")
    st.caption("Agent 执行过程的完整日志，用于调试和审计。")

    if not st.session_state.analysis_done or not st.session_state.agent_state:
        st.info("请先在「分析」Tab 中执行一次分析。")
    else:
        agent_state = st.session_state.agent_state

        col1, col2 = st.columns(2)

        with col1:
            # 完成状态
            st.subheader("✅ 完成状态")
            st.metric("是否完成", "是" if agent_state.get("is_complete") else "否")
            st.metric("已完成步骤数", len(agent_state.get("completed_steps", [])))

            # 已完成的步骤
            completed = agent_state.get("completed_steps", [])
            if completed:
                st.markdown("**已完成步骤:**")
                for s in completed:
                    st.markdown(f"- ✅ `{s}`")

            # 错误信息
            error_msg = agent_state.get("error_message")
            if error_msg:
                st.error(f"**错误:** {error_msg}")
                st.info(f"重试次数: {agent_state.get('retry_count', 0)} / {agent_state.get('max_retries', 2)}")

        with col2:
            # 执行时间
            st.subheader("⏱️ 耗时")
            start = st.session_state.analysis_start_time
            if start:
                elapsed = (datetime.now() - start).total_seconds()
                st.metric("总耗时", f"{elapsed:.1f} 秒")

            # 生成的图表数
            n_figs = len(agent_state.get("figures", {}))
            st.metric("生成图表数", n_figs)

            # 分析计划 vs 完成情况
            plan = agent_state.get("analysis_plan", [])
            if plan:
                df = pd.DataFrame({
                    "步骤": plan,
                    "已完成": ["✅" if s in completed else "⏳" for s in plan],
                })
                st.dataframe(df, use_container_width=True, hide_index=True)

        # 完整 State（JSON 折叠展示）
        st.divider()
        st.subheader("🔍 完整 State（调试用）")

        # 构造可序列化的 state（排除不可序列化内容）
        serializable_state = {}
        for k, v in agent_state.items():
            try:
                json.dumps({k: v})
                serializable_state[k] = v
            except (TypeError, ValueError):
                serializable_state[k] = str(v)

        st.json(serializable_state)

        # 下载 state 按钮
        state_json = json.dumps(serializable_state, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ 下载 State JSON",
            data=state_json,
            file_name=f"spatialmind_state_{st.session_state.session_id[:8]}.json",
            mime="application/json",
            use_container_width=True,
        )


# ── 页脚 ──
st.divider()
st.caption(
    "🧬 SpatialMind — 基于 LangGraph 的空间转录组分析 Agent | "
    "AI 生成内容仅供参考，不构成科学结论。"
)