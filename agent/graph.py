"""
LangGraph 图定义（节点 + 边 + 编译）

图结构：
START → intent_parser → planner → executor → checker →
    ├─ (pass) → explainer → executor (还有步骤) / skill_invoker (全部完成) → END
    ├─ (fail) → error_handler → executor (可重试) / planner (超重试)
    └─ (skip) → executor
"""

from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes.intent_parser import intent_parser_node
from agent.nodes.planner import planner_node
from agent.nodes.executor import executor_node
from agent.nodes.checker import checker_node
from agent.nodes.explainer import explainer_node
from agent.nodes.skill_invoker import skill_invoker_node
from agent.nodes.error_handler import error_handler_node


def should_checker_route(state: AgentState) -> str:
    """
    checker 节点的条件路由。

    返回目标节点名：
        "explainer"      — 结果合理
        "error_handler"  — 结果失败，需重试
        "executor"       — 结果可跳过，继续下一步
    """
    decision = state.get("checker_decision", "pass")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if decision == "pass":
        return "explainer"
    elif decision == "fail" and retry_count < max_retries:
        return "error_handler"
    else:
        # fail 但已无重试次数，或 skip
        return "executor"


def should_error_handler_route(state: AgentState) -> str:
    """
    error_handler 的条件路由

    返回：
        "executor"  — 重试当前步骤
        "planner"   — 超过重试次数，重新规划
    """
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if retry_count < max_retries:
        return "executor"
    else:
        return "planner"


def should_explainer_route(state: AgentState) -> str:
    """
    explainer 的条件路由

    返回：
        "executor"      — 还有未完成步骤
        "skill_invoker" — 所有步骤全部完成
    """
    analysis_plan = state.get("analysis_plan", [])
    completed_steps = state.get("completed_steps", [])

    if all(step in completed_steps for step in analysis_plan):
        return "skill_invoker"
    else:
        return "executor"


def build_graph() -> StateGraph:
    """构建并返回 LangGraph"""
    graph_builder = StateGraph(AgentState)

    # 注册节点
    graph_builder.add_node("intent_parser", intent_parser_node)
    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("executor", executor_node)
    graph_builder.add_node("checker", checker_node)
    graph_builder.add_node("explainer", explainer_node)
    graph_builder.add_node("skill_invoker", skill_invoker_node)
    graph_builder.add_node("error_handler", error_handler_node)

    # 添加边
    graph_builder.add_edge(START, "intent_parser")
    graph_builder.add_edge("intent_parser", "planner")
    graph_builder.add_edge("planner", "executor")
    graph_builder.add_edge("executor", "checker")

    # 条件边
    graph_builder.add_conditional_edges(
        "checker",
        should_checker_route,
        {
            "explainer": "explainer",
            "error_handler": "error_handler",
            "executor": "executor",
        },
    )
    graph_builder.add_conditional_edges(
        "error_handler",
        should_error_handler_route,
        {
            "executor": "executor",
            "planner": "planner",
        },
    )
    graph_builder.add_conditional_edges(
        "explainer",
        should_explainer_route,
        {
            "executor": "executor",
            "skill_invoker": "skill_invoker",
        },
    )
    graph_builder.add_edge("skill_invoker", END)

    return graph_builder


def compile_graph(saverb=None) -> StateGraph:
    """
    编译图并配置持久化。

    使用 MemorySaver 作为默认检查点（跨会话不持久化）。
    需要 Sqlite 持久化时，传入 SqliteSaver.from_conn_string("outputs/checkpoints.db"):
        with SqliteSaver.from_conn_string("outputs/checkpoints.db") as saver:
            app = compile_graph(saver)

    返回可调用的 CompiledGraph。
    """
    from langgraph.checkpoint.memory import MemorySaver

    graph_builder = build_graph()

    # 默认使用 MemorySaver（进程内持久化）
    if saverb is None:
        checkpointer = MemorySaver()
    else:
        checkpointer = saverb

    return graph_builder.compile(checkpointer=checkpointer)


# 全局编译好的图实例
app = compile_graph()