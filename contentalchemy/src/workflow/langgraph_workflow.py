from langgraph.graph import StateGraph, END
from src.workflow.state_management import AgentState
from src.agents.query_handler import query_handler_node
from src.agents.research_agent import research_agent_node
from src.agents.blog_writer import blog_writer_node
from src.agents.linkedin_writer import linkedin_writer_node
from src.agents.image_generator import image_generator_node
from src.agents.content_strategist import content_strategist_node


def route_after_query(state: AgentState) -> str:
    """Routes to first agent after Query Handler."""
    return state["next_agent"]


def chain_router(state: AgentState) -> str:
    """
    Called after each agent finishes.
    If agent_chain has items left, pop the next one and run it.
    Otherwise go to END.
    """
    chain = state.get("agent_chain", [])
    if chain:
        return chain[0]   # next agent in the chain
    return "end"


def pop_chain(state: AgentState) -> AgentState:
    """
    Removes the first item from agent_chain after routing to it.
    Called at the start of each chained agent run.
    """
    chain = state.get("agent_chain", [])
    return {
        **state,
        "agent_chain": chain[1:]  # remove the first item
    }


def build_workflow():
    graph = StateGraph(AgentState)

    # Core nodes
    graph.add_node("query_handler", query_handler_node)
    graph.add_node("research",      research_agent_node)
    graph.add_node("blog",          blog_writer_node)
    graph.add_node("linkedin",      linkedin_writer_node)
    graph.add_node("image",         image_generator_node)
    graph.add_node("strategist",    content_strategist_node)

    # Chain management node — pops the next agent off the chain
    graph.add_node("pop_chain", pop_chain)

    # Entry point → query handler
    graph.set_entry_point("query_handler")

    # After query handler → route to first agent
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

    # After each agent → check if chain has more agents
    for agent in ["research", "blog", "linkedin", "image", "strategist"]:
        graph.add_conditional_edges(
            agent,
            chain_router,
            {
                "research":   "pop_chain",
                "blog":       "pop_chain",
                "linkedin":   "pop_chain",
                "image":      "pop_chain",
                "strategist": "pop_chain",
                "end":        END,
            }
        )

    # After popping chain → route to next agent
    graph.add_conditional_edges(
        "pop_chain",
        lambda s: s["agent_chain"][0] if s["agent_chain"] else s["next_agent"],
        {
            "research":   "research",
            "blog":       "blog",
            "linkedin":   "linkedin",
            "image":      "image",
            "strategist": "strategist",
        }
    )

    return graph.compile()


workflow = build_workflow()