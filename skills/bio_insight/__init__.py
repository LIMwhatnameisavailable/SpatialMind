"""BioInsightSkill 入口"""
from skills.bio_insight.cluster_namer import name_clusters
from skills.bio_insight.spatial_story import generate_spatial_story
from skills.bio_insight.insight_extractor import extract_insights

def run_bio_insight_skill(state: dict) -> dict:
    outputs = {}
    try:
        outputs["cluster_names"] = name_clusters(state)
    except Exception as e:
        outputs["cluster_names"] = {"error": str(e)}
    try:
        outputs["spatial_story"] = generate_spatial_story(state)
    except Exception as e:
        outputs["spatial_story"] = f"空间叙事生成失败: {e}"
    try:
        outputs["insights"] = extract_insights(state)
    except Exception as e:
        outputs["insights"] = f"关键发现提取失败: {e}"
    outputs["disclaimer"] = "AI生成内容，仅供参考，不构成科学结论。"
    skill_outputs = dict(state.get("skill_outputs", {}))
    skill_outputs["bio_insight"] = outputs
    return {**state, "skill_outputs": skill_outputs}