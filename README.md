# 🧬 SpatialMind: LangGraph-Powered Spatial Transcriptomics Analysis Agent

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2%2B-orange)]()
[![Scanpy](https://img.shields.io/badge/Scanpy-1.11%2B-green)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red)]()

**SpatialMind** is an intelligent agent for spatial transcriptomics data analysis built on [LangGraph](https://langchain-ai.github.io/langgraph/). It accepts natural language instructions, dynamically plans and executes a Scanpy/Squidpy-based analysis pipeline, and delivers publication-level figures with biological insights through two specialized Skill modules.

---

## 🌐 Online Demo

**http://47.101.68.210:8501**

> ⚠️ The demo server is a lightweight instance (4 GB RAM) for course demonstration purposes. It may be rate-limited or unavailable after the course period. SVG analysis is disabled by default on this server due to memory constraints.

---

## ✨ Core Capabilities

| Capability | Description |
|-----------|-------------|
| **🧠 Knowledge QA** | Ask questions like *"What is spatial transcriptomics?"* — no data upload needed |
| **🔬 Full Analysis** | Upload a `.h5ad` file and say *"Run full analysis"* — the agent plans and executes all steps |
| **📊 Targeted Analysis** | Request specific workflows: *"Only QC and clustering"*, *"Find marker genes"* |
| **📝 Journal-Style Output** | Auto-generate Nature-style Methods paragraphs and figure captions |
| **🔬 Biological Insights** | Cluster naming, spatial story, and key findings extraction |
| **🖼️ Figure Gallery** | Browse all generated figures grouped by analysis step |
| **💡 Agent Thinking Display** | Visualize the LangGraph node execution path and Planner reasoning |

---

## 🏗️ Architecture: LangGraph Agent

SpatialMind is built as a **stateful LangGraph agent** with the following node structure:

```
User Input → intent_parser → planner → executor ↔ checker ↔ error_handler → explainer → skill_invoker → Output
```

| Node | File | LLM? | Responsibility |
|------|------|:----:|---------------|
| **intent_parser** | `agent/nodes/intent_parser.py` | ✅ | Classify intent: QA / no_data / analysis; extract data path and parameters |
| **planner** | `agent/nodes/planner.py` | ✅ (Thinking) | Generate an ordered list of analysis steps using LLM reasoning |
| **executor** | `agent/nodes/executor.py` | ❌ | Execute the next step by calling the appropriate tool function |
| **checker** | `agent/nodes/checker.py` | ✅ | Validate tool output — decide pass / retry / skip |
| **error_handler** | `agent/nodes/error_handler.py` | ❌ | Record errors, manage retry logic, or re-plan |
| **explainer** | `agent/nodes/explainer.py` | ✅ | Generate human-readable explanations for each step result |
| **skill_invoker** | `agent/nodes/skill_invoker.py` | ✅ | Invoke BioInsightSkill and NaturePublishSkill after analysis completes |

### Conditional Routing

The graph uses dynamic routing:
- `checker → explainer` (pass) | `checker → error_handler` (fail, retry available) | `checker → executor` (skip)
- `explainer → executor` (more steps remain) | `explainer → skill_invoker` (all steps done)
- `error_handler → executor` (retry with updated params) | `error_handler → planner` (exhausted retries, re-plan)

---

## 🔬 Default Analysis Pipeline

When the user requests a full analysis without specifying steps, the agent executes:

```
data_load → qc → preprocess → dimred → cluster → spatial → marker
```

| Step | Tool | Output |
|------|------|--------|
| **data_load** | `data_loader.py` | Data summary (n_obs, n_vars) |
| **qc** | `qc.py` | QC violin plots, QC metrics |
| **preprocess** | `preprocessing.py` | Normalization, log1p, HVG selection, scaling |
| **dimred** | `dimred.py` | PCA elbow plot, UMAP embedding |
| **cluster** | `clustering.py` | Leiden clustering, cluster size distribution |
| **spatial** | `spatial_viz.py` | Spatial cluster distribution, gene expression spatial plots |
| **marker** | `marker_genes.py` | Marker gene dotplot, marker UMAP |

> **SVG analysis** (spatially variable genes) is a compute-intensive extension and is only triggered when the user explicitly mentions *"spatially variable genes"*, *"SVG"*, or *"Moran's I"*.

---

## 🛠️ Skills Modules

### BioInsightSkill
- **Cluster Namer**: Assigns biological identities to clusters via LLM + marker gene reference
- **Spatial Story**: Generates narrative text describing spatial organization
- **Insight Extractor**: Summarizes key findings from the analysis
- *All outputs include: "AI-generated content, for reference only — not a scientific conclusion"*

### NaturePublishSkill
- **Panel Composer**: Arranges figures into publication-ready multi-panel layouts
- **Caption Writer**: Generates Nature-style figure captions
- **Methods Writer**: Produces Methods paragraphs following journal style
- **HTML Report**: Exports a complete analysis report as a self-contained HTML file

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- 8 GB+ RAM recommended (4 GB minimum for basic analysis)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd SpatialMind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (see below)
```

### Environment Variables

Create `.env` in the project root:

```env
PPIO_API_KEY=your_api_key_here
PPIO_BASE_URL=https://api.ppio.com/anthropic
LLM_MODEL_NAME=deepseek/deepseek-v4-flash
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PPIO_API_KEY` | ✅ | — | API key for the LLM provider |
| `PPIO_BASE_URL` | ❌ | `https://api.ppio.com/anthropic` | LLM API endpoint base URL |
| `LLM_MODEL_NAME` | ❌ | `deepseek/deepseek-v4-flash` | Model name to use |

### Data

SpatialMind supports **`.h5ad`** files from Visium, Stereo-seq, and other spatial transcriptomics platforms. You can either:
1. Upload a file via the Streamlit sidebar (recommended for the web interface)
2. Place a file in `data/` and reference its path

> **GSE278603** data is recommended for testing. Please download it separately — large data files are not included in this repository.

---

## 🚀 Usage Examples

Once the server is running (`streamlit run app.py`), try these prompts:

| Prompt | Expected Behavior |
|--------|------------------|
| *"What is spatial transcriptomics?"* | Agent answers directly (no data required) |
| *"What is the difference between Visium and Stereo-seq?"* | Agent answers directly |
| *"Run full analysis"* | Prompt to upload `.h5ad`, then execute all 7 steps |
| *"Only QC and clustering"* | Run only QC and Leiden clustering steps |
| *"Full analysis with Nature-style figure captions"* | Full analysis + NaturePublishSkill outputs |
| *"Find spatially variable genes"* | SVG analysis (compute-intensive, skip on light server) |

---

## 📊 Output Gallery

Analysis results include:

- **QC Violin Plots**: Gene count, UMI count, mitochondrial percentage per cell
- **PCA Elbow Plot**: Variance explained by principal components
- **UMAP Embedding**: Cell clusters visualized in 2D
- **Leiden Clusters**: Cluster membership with spatial coordinates
- **Spatial Gene Expression**: Gene expression mapped onto tissue coordinates
- **Marker Gene Dotplot**: Top marker genes per cluster
- **Methods Paragraph**: Auto-generated, journal-style methodology text
- **Figure Captions**: Nature-style captions for each figure

All figures are accessible in the **Figure Gallery** tab and can be downloaded individually.

---

## 📁 Project Structure

```
SpatialMind/
├── app.py                          # Streamlit frontend (5 tabs)
├── CLAUDE.md                       # Development guidelines
├── ARCHITECTURE.md                 # Agent architecture documentation
├── SKILLS.md                       # Skills module specifications
├── PROMPTS.md                      # LLM prompt templates
├── DATA_SCHEMA.md                  # Data field documentation
├── PLOT_GUIDE.md                   # Plotting style guide
├── requirements.txt                # Python dependencies
│
├── agent/                          # LangGraph agent core
│   ├── graph.py                    # Graph definition (nodes + edges + compile)
│   ├── state.py                    # AgentState TypedDict
│   ├── llm_client.py               # Unified LLM client (Anthropic SDK)
│   └── nodes/                      # One file per node
│       ├── intent_parser.py
│       ├── planner.py
│       ├── executor.py
│       ├── checker.py
│       ├── skill_invoker.py
│       ├── explainer.py
│       └── error_handler.py
│
├── tools/                          # Analysis tools (NO LLM calls)
│   ├── data_loader.py
│   ├── qc.py
│   ├── preprocessing.py
│   ├── dimred.py
│   ├── clustering.py
│   ├── spatial_viz.py
│   ├── marker_genes.py
│   ├── svg.py
│   └── plot_style.py
│
├── skills/                         # Skills modules
│   ├── nature_publish/             # NaturePublishSkill
│   │   ├── palette.py
│   │   ├── panel_composer.py
│   │   ├── caption_writer.py
│   │   ├── methods_writer.py
│   │   └── html_report.py
│   └── bio_insight/                # BioInsightSkill
│       ├── cluster_namer.py
│       ├── spatial_story.py
│       ├── qc_interpreter.py
│       ├── insight_extractor.py
│       └── lit_reader.py
│
├── data/                           # Data directory (not committed)
│   └── schema/                     # Data schema definitions
│
├── outputs/                        # Generated outputs (not committed)
│   ├── figures/
│   └── reports/
│
└── tests/                          # Unit tests
    ├── test_tools.py
    ├── test_skills.py
    └── test_graph.py
```

---

## 🖥️ Deployment

### systemd Service (Linux)

```ini
[Unit]
Description=SpatialMind Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/SpatialMind
Environment="PATH=/path/to/SpatialMind/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/path/to/SpatialMind/venv/bin/streamlit run /path/to/SpatialMind/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5
MemoryMax=2800M
MemoryHigh=2400M

[Install]
WantedBy=multi-user.target
```

### Memory Considerations
- **Lightweight server (4 GB RAM)**: SVG analysis disabled by default. ~2 GB swap recommended.
- **Workstation (16 GB+ RAM)**: Full analysis including SVG runs comfortably. Use `flavor='igraph'` for faster Leiden clustering.

---

## 🎓 Course Project

This is the final project for a **Computational Biology** course at Southeast University. It demonstrates:

- **LangGraph Agent Architecture**: Stateful, graph-based agent orchestration with dynamic routing
- **Tool Calling Integration**: 9 analysis tools wrapping Scanpy/Squidpy
- **LLM-Augmented Outputs**: Natural language explanations, cluster naming, journal-style writing
- **State Management**: LangGraph checkpoint persistence, session-aware output management
- **Interactive UI**: Streamlit-based frontend with 5 functional tabs

---

## ⚠️ Disclaimer

- AI-generated biological interpretations, cluster names, and insights are for **reference only** and should not replace domain expert validation.
- All scientific conclusions must be verified through proper experimental validation.
- The online demo is for **educational purposes** and may not be continuously available.

---

## 📄 License

This project is provided for educational use as part of the SEU Computational Biology course.

---

*Built with [LangGraph](https://langchain-ai.github.io/langgraph/), [Scanpy](https://scanpy.readthedocs.io/), [Squidpy](https://squidpy.readthedocs.io/), and [Streamlit](https://streamlit.io/)*
