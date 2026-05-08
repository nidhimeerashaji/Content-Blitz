from langgraph.graph import StateGraph, END
from src.workflow.state_management import AgentState
from src.agents.query_handler import query_handler_node

def route_after_query(state: AgentState) -> str:
    """
    Called by LangGraph after Query Handler runs.
    Returns the name of the next node to visit.
    """
    return state["next_agent"]


def build_workflow():
    graph = StateGraph(AgentState)

    # Add the query handler as a node
    graph.add_node("query_handler", query_handler_node)

    # Placeholder nodes for Phase 3 agents
    graph.add_node("research",   lambda s: {**s, "final_output": "Research agent coming in Phase 3"})
    graph.add_node("blog",       lambda s: {**s, "final_output": "Blog agent coming in Phase 3"})
    graph.add_node("linkedin",   lambda s: {**s, "final_output": "LinkedIn agent coming in Phase 3"})
    graph.add_node("image",      lambda s: {**s, "final_output": "Image agent coming in Phase 3"})
    graph.add_node("strategist", lambda s: {**s, "final_output": "Strategist agent coming in Phase 3"})

    # Entry point
    graph.set_entry_point("query_handler")

    # Conditional routing
    graph.add_conditional_edges(
        "query_handler",
        route_after_query,
        {
            "research":   "research",
            "blog":       "blog",
            "linkedin":   "linkedin",
            "image":      "image",
            "strategist": "strategist",
        }
    )

    # All agents lead to END
    for agent in ["research", "blog", "linkedin", "image", "strategist"]:
        graph.add_edge(agent, END)

    return graph.compile()


# ← THIS LINE IS CRITICAL — creates the workflow object
workflow = build_workflow()