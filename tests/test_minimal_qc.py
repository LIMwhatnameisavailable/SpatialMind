"""
最小闭环测试 v2：验证 LangGraph 图能正确执行 data_load + qc 两步
"""
import sys
sys.path.insert(0, ".")

from agent.graph import compile_graph
import uuid


def test_minimal_qc():
    graph = compile_graph()

    initial_state = {
        "user_input": "请对 Visium 数据执行 QC 分析",
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

    print("=== 测试: data_load + qc 两步 ===")
    print("input:", initial_state["user_input"])
    print()
    try:
        result = graph.invoke(initial_state, config=config)
        print("PASS: 图执行完成")
        print("completed_steps:", result.get("completed_steps"))
        print("is_complete:", result.get("is_complete"))

        print("\n=== 生成的文件 ===")
        step_results = result.get("step_results", {})
        for step, sr in step_results.items():
            fpaths = sr.get("figure_paths", [])
            print(f"  [{step}] 图数量: {len(fpaths)}")
            for fp in fpaths:
                print(f"    -> {fp}")

        print("\n=== 结果摘要 ===")
        for step, sr in step_results.items():
            print(f"  [{step}] {sr.get('summary', '')}")

        print("\n=== 解释 ===")
        explanations = result.get("explanations", {})
        for step, exp in explanations.items():
            print(f"  [{step}] {exp[:150]}...")

    except Exception as e:
        print(f"FAIL: 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_minimal_qc()