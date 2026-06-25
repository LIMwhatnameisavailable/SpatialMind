"""Skills 包 — 对外暴露两个 Skill 的入口函数"""
try:
    from skills.nature_publish import run_nature_publish_skill
except Exception:
    def run_nature_publish_skill(state):
        return state

try:
    from skills.bio_insight import run_bio_insight_skill
except Exception:
    def run_bio_insight_skill(state):
        return state

__all__ = ["run_nature_publish_skill", "run_bio_insight_skill"]