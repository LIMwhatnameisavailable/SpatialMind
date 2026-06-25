"""
html_report.py — HTML 报告生成

将分析结果、图表内嵌到独立可分享的 HTML 文件中。
"""

import os
import base64
from datetime import datetime
from agent.state import AgentState


def _img_to_base64(path: str) -> str:
    """将图片转为 base64 data URI"""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = f.read()
    ext = path.split(".")[-1]
    encoded = base64.b64encode(data).decode()
    return f"data:image/{ext};base64,{encoded}"


def generate_html_report(state: AgentState) -> str:
    """
    生成独立的 HTML 分析报告。

    Args:
        state: AgentState

    Returns:
        HTML 文件路径
    """
    step_results = state.get("step_results", {})
    explanations = state.get("explanations", {})
    figures = state.get("figures", {})
    skill_outputs = state.get("skill_outputs", {})
    nature_out = skill_outputs.get("nature_publish", {})

    # 构建 HTML
    sections_html = ""

    for step in ["qc", "preprocess", "dimred", "cluster", "spatial", "marker"]:
        if step not in step_results:
            continue
        result = step_results[step]

        img_html = ""  # 默认空字符串
        if step in figures and os.path.exists(figures[step]):
            img_b64 = _img_to_base64(figures[step])
            img_html = f'<img src="{img_b64}" style="max-width:700px;border:1px solid #ddd;border-radius:4px;padding:5px;" />'

        sections_html += f"""
            <div class="section">
                <h2>{step.upper()}</h2>
                <p><strong>摘要:</strong> {result.get('summary', '')}</p>
                <div class="metrics">
                    <pre>{result.get('metrics', {})}</pre>
                </div>
                {img_html}
                <p class="explanation">{explanations.get(step, '')}</p>
            </div>
            """

    methods_html = ""
    if nature_out and nature_out.get("methods"):
        methods_html = f"""
        <div class="section">
            <h2>Methods</h2>
            <p>{nature_out['methods']}</p>
        </div>
        """

    captions_html = ""
    if nature_out and nature_out.get("captions"):
        captions_html = f"""
        <div class="section">
            <h2>Figure Legends</h2>
            <p>{nature_out['captions']}</p>
        </div>
        """

    # BioInsight
    bio_out = skill_outputs.get("bio_insight", {})
    bio_html = ""
    if bio_out:
        if bio_out.get("spatial_story"):
            bio_html += f"""
            <div class="section">
                <h2>Spatial Story</h2>
                <p>{bio_out['spatial_story']}</p>
            </div>
            """
        if bio_out.get("qc_interpretation"):
            bio_html += f"""
            <div class="section">
                <h2>QC Interpretation</h2>
                <p>{bio_out['qc_interpretation']}</p>
            </div>
            """
        if bio_out.get("insights"):
            bio_html += f"""
            <div class="section">
                <h2>Key Insights</h2>
                <p>{bio_out['insights']}</p>
                <p class="disclaimer"><em>{bio_out.get('disclaimer', '')}</em></p>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpatialMind Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metrics {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
        }}
        .explanation {{
            color: #555;
            font-style: italic;
        }}
        .disclaimer {{
            color: #999;
            font-size: 0.85em;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            color: #888;
            font-size: 0.8em;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <h1>SpatialMind Analysis Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Data Type: {state.get('data_type', 'unknown')}</p>
    <p>Data Path: {state.get('data_path', 'N/A')}</p>

    {sections_html}
    {methods_html}
    {captions_html}
    {bio_html}

    <div class="footer">
        <p>Generated by SpatialMind — Spatial Transcriptomics Analysis Agent</p>
        <p class="disclaimer">AI-generated content is for reference only and does not constitute scientific conclusions.</p>
    </div>
</body>
</html>"""

    os.makedirs("outputs/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"outputs/reports/report_{timestamp}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html_path