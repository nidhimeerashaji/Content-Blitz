from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Conversation history
    messages: Annotated[list, add_messages]

    # User's original message
    user_input: str

    # Primary agent to run
    next_agent: str

    # NEW — chain of agents to run after the primary one
    # e.g. ["blog"] means after research, run blog writer
    agent_chain: list[str]

    # Extracted topic
    topic: str

    # Agent outputs
    research_output: Optional[str]
    blog_output: Optional[str]
    linkedin_output: Optional[str]
    image_prompt: Optional[str]
    final_output: Optional[str]

    # Error tracking
    error: Optional[str]