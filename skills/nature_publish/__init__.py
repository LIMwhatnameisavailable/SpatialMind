"""NaturePublishSkill 入口"""
from skills.nature_publish.html_report import generate_html_report
from skills.nature_publish.caption_writer import write_captions
from skills.nature_publish.methods_writer import write_methods
from skills.nature_publish.word_exporter import export_word

def run_nature_publish_skill(state: dict) -> dict:
    outputs = {}
    try:
        outputs["captions"] = write_captions(state)
    except Exception as e:
        outputs["captions"] = f"图注生成失败: {e}"
    try:
        outputs["methods"] = write_methods(state)
    except Exception as e:
        outputs["methods"] = f"Methods生成失败: {e}"
    try:
        outputs["html_report"] = generate_html_report(state)
    except Exception as e:
        outputs["html_report"] = ""
    try:
        word_result = export_word(state)
        outputs["docx_path"] = word_result.get("docx_path", "")
    except Exception as e:
        outputs["docx_path"] = ""
    outputs["disclaimer"] = "AI生成内容，仅供参考。"
    skill_outputs = dict(state.get("skill_outputs", {}))
    skill_outputs["nature_publish"] = outputs
    return {**state, "skill_outputs": skill_outputs}