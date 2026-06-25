"""
LangGraph 图定义（节点 + 边 + 编译）

图结构：
START → intent_parser →
    ├─ (qa)       → END
    └─ (analysis) → planner → executor → checker →
           ├─ (pass) → explainer → executor / skill_invoker → END
           ├─ (fail) → error_handler → executor / planner
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


def should_intent_route(state: AgentState) -> str:
    """intent_parser 后的路由：qa/no_data 直接结束，analysis 进入 planner"""
    request_type = state.get("request_type", "")
    if request_type in ("qa", "no_data", "result_explanation") or state.get("is_complete", False):
        return "__end__"
    return "planner"


def should_checker_route(state: AgentState) -> str:
    decision = state.get("checker_decision", "pass")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if decision == "pass":
        return "explainer"
    elif decision == "fail" and retry_count < max_retries:
        return "error_handler"
    else:
        return "executor"


def should_error_handler_route(state: AgentState) -> str:
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    if retry_count < max_retries:
        return "executor"
    else:
        return "planner"


def should_explainer_route(state: AgentState) -> str:
    analysis_plan = state.get("analysis_plan", [])
    completed_steps = state.get("completed_steps", [])
    if all(step in completed_steps for step in analysis_plan):
        return "skill_invoker"
    else:
        return "executor"


def build_graph() -> StateGraph:
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("intent_parser", intent_parser_node)
    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("executor", executor_node)
    graph_builder.add_node("checker", checker_node)
    graph_builder.add_node("explainer", explainer_node)
    graph_builder.add_node("skill_invoker", skill_invoker_node)
    graph_builder.add_node("error_handler", error_handler_node)

    graph_builder.add_edge(START, "intent_parser")

    # intent_parser 后的条件路由（qa/no_data → END，analysis → planner）
    graph_builder.add_conditional_edges(
        "intent_parser",
        should_intent_route,
        {"planner": "planner", "__end__": END},
    )

    # planner ååå¤æ­ï¼ç©ºè®¡åâENDï¼æ­£å¸¸âexecutor
    graph_builder.add_conditional_edges(
        "planner",
        lambda s: "__end__" if not s.get("analysis_plan", []) or s.get("is_complete", False) else "executor",
        {"executor": "executor", "__end__": END},
    )

    graph_builder.add_edge("executor", "checker")

    graph_builder.add_conditional_edges(
        "checker",
        should_checker_route,
        {"explainer": "explainer", "error_handler": "error_handler", "executor": "executor"},
    )
    graph_builder.add_conditional_edges(
        "error_handler",
        should_error_handler_route,
        {"executor": "executor", "planner": "planner"},
    )
    graph_builder.add_conditional_edges(
        "explainer",
        should_explainer_route,
        {"executor": "executor", "skill_invoker": "skill_invoker"},
    )
    graph_builder.add_edge("skill_invoker", END)

    return graph_builder


def compile_graph(saverb=None) -> StateGraph:
    from langgraph.checkpoint.memory import MemorySaver
    graph_builder = build_graph()
    checkpointer = saverb if saverb is not None else MemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)


app = compile_graph()
