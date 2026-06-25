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

# ── 自定义 CSS（深色科技风） ──
st.markdown("""
<style>
/* 全局背景 */
.stApp { background-color: #0f1117; }

/* 侧边栏 */
[data-testid="stSidebar"] { background-color: #1a1d2e; }
[data-testid="stSidebar"] .stMarkdown { color: #c8d0e0; }

/* 主内容卡片 */
[data-testid="stVerticalBlock"] > div {
    background-color: transparent;
}

/* Tab样式 */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1e2130;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #8892a4;
    border-radius: 6px;
}
.stTabs [aria-selected="true"] {
    background-color: #00d4aa22;
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa;
}

/* 按钮 */
.stButton > button {
    background-color: #00d4aa;
    color: #0f1117;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: #00b894;
    transform: translateY(-1px);
}

/* 输入框 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1e2130;
    color: #e0e6f0;
    border: 1px solid #2d3250;
    border-radius: 6px;
}

/* 成功/错误消息 */
.stSuccess { border-left: 4px solid #00d4aa; background-color: #00d4aa11; }
.stError { border-left: 4px solid #ff6b6b; background-color: #ff6b6b11; }
.stInfo { border-left: 4px solid #4dabf7; background-color: #4dabf711; }
.stWarning { border-left: 4px solid #ffd43b; background-color: #ffd43b11; }

/* 进度条 */
.stProgress > div > div > div { background-color: #00d4aa; }

/* 通用文字 */
.stMarkdown, p, span, label { color: #c8d0e0; }
h1, h2, h3 { color: #e8edf5 !important; }

/* 图片容器 */
[data-testid="stImage"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #2d3250;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #1e2130;
    border: 1px solid #2d3250;
    border-radius: 8px;
}

/* 侧边栏卡片 & Step卡片（复用） */
.step-card {
    background-color: #1e2130 !important;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    border: 1px solid #2d3250;
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


# ══════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════

def get_step_name_from_filename(filename: str) -> str:
    """从图片文件名推断步骤名"""
    name = filename.lower()
    for step in ["qc", "preprocess", "dimred", "cluster", "spatial", "marker", "svg"]:
        if name.startswith(step):
            return step
    return "other"


def discover_figures() -> dict[str, list[dict]]:
    """
    扫描 outputs/figures/ 目录下的所有 PNG 图片。
    返回按步骤分组的字典: {step_name: [{path, filename, mtime}, ...]}
    """
    groups: dict[str, list[dict]] = {}
    if not FIGURES_DIR.exists():
        return groups

    # 同时扫描根目录和 archive/ 子目录
    for root, _dirs, files in os.walk(str(FIGURES_DIR)):
        for fname in sorted(files):
            if not fname.endswith(".png"):
                continue
            fpath = os.path.join(root, fname)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            step = get_step_name_from_filename(fname)
            groups.setdefault(step, []).append({
                "path": fpath,
                "filename": fname,
                "mtime": mtime.strftime("%Y-%m-%d %H:%M:%S"),
            })
    return groups


# ══════════════════════════════════════════
# 侧边栏
# ══════════════════════════════════════════
with st.sidebar:
    st.sidebar.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2em;'>🧬</div>
        <div style='font-size:1.3em; font-weight:700; color:#00d4aa;'>SpatialMind</div>
        <div style='font-size:0.75em; color:#8892a4; margin-top:4px;'>空间转录组智能分析平台</div>
    </div>
    <hr style='border-color:#2d3250; margin:8px 0;'>
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
    st.sidebar.markdown("### 🎨 Skills 设置")
    enable_nature_publish = st.sidebar.toggle("🎨 NaturePublish 模式", value=True, key="toggle_nature")
    enable_bio_insight = st.sidebar.toggle("🧠 BioInsight 洞察", value=True, key="toggle_bio")

    st.divider()
    st.caption(f"会话 `{st.session_state.session_id[:8]}...`")
    if st.session_state.data_loaded:
        st.success("✅ 数据已加载")
    else:
        st.info("⏳ 数据未加载")


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
        run_clicked = st.button("🚀 开始分析", type="primary", use_container_width=True)
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

                # 2 列布局：最多显示 2 张图
                if step in figures:
                    fig_path = figures[step]
                    if os.path.exists(fig_path):
                        # 尝试从 step_results 获取更多图片
                        extra_figs = step_results.get(step, {}).get("figure_paths", [])
                        extra_figs = [f for f in extra_figs if f != fig_path and os.path.exists(f)]

                        cols = st.columns(2)
                        with cols[0]:
                            st.image(fig_path, caption=f"{step.upper()} — 主图", use_container_width=True)

                        with cols[1]:
                            if extra_figs:
                                st.image(extra_figs[0], caption=f"{step.upper()} — 辅助图", use_container_width=True)
                            else:
                                # 第二列展示关键指标
                                metrics = step_results.get(step, {}).get("metrics", {})
                                if metrics:
                                    st.markdown("**📈 关键指标**")
                                    for k, v in metrics.items():
                                        if isinstance(v, (int, float)):
                                            st.metric(label=k.replace("_", " ").title(), value=f"{v:.4f}" if isinstance(v, float) else str(v))
                                        elif isinstance(v, str):
                                            st.markdown(f"- **{k}:** {v}")
                                        else:
                                            st.markdown(f"- **{k}:** {v}")
                                    st.markdown("")  # spacing
                            # 额外指标 expander
                            metrics = step_results.get(step, {}).get("metrics", {})
                            if metrics and not extra_figs:
                                pass  # already shown above
                            elif metrics:
                                with st.expander("📈 关键指标", expanded=False):
                                    st.json(metrics)
                    else:
                        st.warning(f"图表文件不存在: {fig_path}")
                else:
                    # 没有图片时，全宽展示指标
                    metrics = step_results.get(step, {}).get("metrics", {})
                    if metrics:
                        st.markdown("**📈 关键指标**")
                        st.json(metrics)

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
# Tab 2 · 图表库
# ══════════════════════════════════════════
with tab2:
    st.header("🖼️ 图表库")
    st.caption("浏览 outputs/figures/ 目录下所有已生成的图表。")

    fig_groups = discover_figures()

    if not fig_groups:
        st.info("暂无图表。执行一次分析后会自动生成。")
    else:
        # 按步骤分组展示
        step_display_names = {
            "qc": "QC 质控",
            "preprocess": "预处理",
            "dimred": "降维",
            "cluster": "聚类",
            "spatial": "空间可视化",
            "marker": "Marker 基因",
            "svg": "空间可变基因",
            "panel": "组合排版",
            "other": "其他",
        }

        for step in ["qc", "preprocess", "dimred", "cluster", "spatial", "marker", "svg", "panel", "other"]:
            if step not in fig_groups:
                continue
            images = fig_groups[step]
            display_name = step_display_names.get(step, step.upper())

            with st.expander(f"{display_name}（{len(images)} 张）", expanded=True):
                # 每行 3 列
                cols = st.columns(3)
                for i, img in enumerate(images):
                    col = cols[i % 3]
                    with col:
                        st.image(img["path"], use_container_width=True)
                        st.caption(f"📄 {img['filename']}")
                        st.caption(f"🕒 {img['mtime']}")
                        with open(img["path"], "rb") as fh:
                            st.download_button(
                                label="⬇️ 下载",
                                data=fh,
                                file_name=img["filename"],
                                mime="image/png",
                                key=f"dl_{step}_{i}",
                                use_container_width=True,
                            )


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
                "<div style='text-align:center; color:#00d4aa; font-size:1.5rem;'>→</div>",
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

            # ── 排版图 ──
            panel_paths = nature.get("panel_paths", [])
            if panel_paths:
                st.divider()
                st.subheader("🖼️ 排版图")
                for p in panel_paths:
                    if os.path.exists(p):
                        st.image(p, caption=Path(p).name, use_container_width=True)

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