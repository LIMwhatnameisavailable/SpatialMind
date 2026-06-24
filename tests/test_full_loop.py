"""
完整 Loop 测试：验证 LangGraph 图能否执行多步分析
包含 checker + error_handler + 多步执行
"""
import sys
sys.path.insert(0, ".")

from agent.graph import compile_graph
import uuid


def test_full_loop():
    graph = compile_graph()

    initial_state = {
        "user_input": "请对 Visium 数据执行完整分析：QC、预处理、降维、聚类和空间可视化",
        "session_id": str(uuid.uuid4()),
        "data_path": "data/data/anndata/visium_hne_adata.h5ad",
        "data_type": "visium",
        "adata_cache_key": "",
        "analysis_plan": [],
        "current_step": "",
        "completed_steps": [],
        "step_params": {},
        "figures": {},
        "step_results": {},
        "explanations": {},
        "skill_outputs": {},
        "error_message": None,
        "retry_count": 0,
        "max_retries": 2,
        "is_complete": False,
        "messages": [],
    }

    config = {"configurable": {"thread_id": initial_state["session_id"]}}

    print("=== 开始完整 Loop 测试 ===")
    print("input:", initial_state["user_input"])
    print()
    try:
        result = graph.invoke(initial_state, config=config)
        print("PASS: 图执行完成")
        print("completed_steps:", result.get("completed_steps"))
        print("is_complete:", result.get("is_complete"))
        print("error_message:", result.get("error_message"))

        print("\n=== 各步骤图表 ===")
        figures = result.get("figures", {})
        for step, fig in figures.items():
            print(f"  [{step}]: {fig}")

        print("\n=== 各步骤结果摘要 ===")
        step_results = result.get("step_results", {})
        for step, sr in step_results.items():
            print(f"  [{step}] {sr.get('summary', '')[:120]}")

        print("\n=== 各步骤解释 ===")
        explanations = result.get("explanations", {})
        for step, exp in explanations.items():
            print(f"  [{step}] {exp[:150]}...")

        print("\n=== Skills 输出 ===")
        skill_outputs = result.get("skill_outputs", {})
        for skill_name, output in skill_outputs.items():
            print(f"  [{skill_name}]: {list(output.keys())}")

    except Exception as e:
        print(f"FAIL: 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_full_loop()