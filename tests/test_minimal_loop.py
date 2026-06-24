"""
最小闭环测试：验证 LangGraph 图能否正确执行单步分析
使用 Visium 数据，只执行 data_load 这一步
"""
import sys
sys.path.insert(0, ".")

from agent.graph import compile_graph
from agent.state import AgentState
import uuid

def test_minimal():
    graph = compile_graph()

    initial_state = {
        "user_input": "请读取 Visium 数据并显示基本信息",
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

    print("=== 开始最小闭环测试 ===")
    try:
        result = graph.invoke(initial_state, config=config)
        print("PASS: 图执行完成")
        print("completed_steps:", result.get("completed_steps"))
        print("is_complete:", result.get("is_complete"))
        print("figures:", list(result.get("figures", {}).keys()))
        print("error_message:", result.get("error_message"))
        if result.get("explanations"):
            for step, exp in result["explanations"].items():
                print(f"\n[{step}] 解释: {exp[:200]}...")
    except Exception as e:
        print(f"FAIL: 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal()