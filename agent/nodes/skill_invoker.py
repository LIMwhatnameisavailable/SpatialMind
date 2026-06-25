"""
skill_invoker 节点 — 在分析完成后调用 Skills 层

职责：
1. 所有分析步骤完成后被调用
2. 根据 state 中的配置决定调用哪些 Skill
3. 调用 NaturePublishSkill 和/或 BioInsightSkill
4. 将输出写入 state.skill_outputs
"""

from agent.state import AgentState


def skill_invoker_node(state: AgentState) -> dict:
    """在分析全部完成后调用 Skills 层"""
    skill_outputs: dict = {}

    # 1. 调用 BioInsightSkill — 生物学洞察
    #   (cluster_namer + spatial_story + qc_interpreter + insight_extractor)
    try:
        from skills.bio_insight.cluster_namer import name_clusters
        from skills.bio_insight.spatial_story import generate_spatial_story
        from skills.bio_insight.insight_extractor import extract_insights

        cluster_result = name_clusters(state)
        spatial_story = generate_spatial_story(state)
        insights = extract_insights(state)

        skill_outputs["bio_insight"] = {
            "cluster_names": cluster_result.get("cluster_names_raw", ""),
            "spatial_story": spatial_story,
            "qc_interpretation": "",   # qc_interpreter 模块暂不启用，留空
            "insights": insights,
            "disclaimer": "AI 生成内容，仅供参考，不构成科学结论。",
        }
    except Exception as e:
        skill_outputs["bio_insight"] = {
            "error": f"BioInsightSkill 执行失败: {e}",
            "disclaimer": "AI 生成内容，仅供参考。",
        }

    # 2. 调用 NaturePublishSkill — 发表级结果输出
    try:
        from skills.nature_publish.panel_composer import compose_panels
        from skills.nature_publish.caption_writer import write_captions
        from skills.nature_publish.methods_writer import write_methods
        from skills.nature_publish.html_report import generate_html_report

        figures = state.get("figures", {})
        captions = ""
        methods = ""

        if figures:
            compose_panels(state)
            captions = write_captions(state)
            methods = write_methods(state)

        # 先构建包含 bio_insight 的临时 state，再传给 generate_html_report
        state_with_bio = dict(state)
        state_with_bio["skill_outputs"] = skill_outputs
        html_path = generate_html_report(state_with_bio)

        skill_outputs["nature_publish"] = {
            "captions": captions,
            "methods": methods,
            "html_report": html_path,
            "disclaimer": "AI 生成内容，仅供参考。",
        }
    except ImportError as e:
        skill_outputs["nature_publish"] = {
            "error": f"NaturePublishSkill 加载失败: {e}",
        }

    return {
        "skill_outputs": skill_outputs,
        "is_complete": True,
    }