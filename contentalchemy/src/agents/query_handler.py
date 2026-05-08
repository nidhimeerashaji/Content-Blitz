import json
import anthropic
from src.core.config import config
from src.workflow.state_management import AgentState

client = anthropic.Anthropic(api_key=config.anthropic_api_key)

ROUTER_PROMPT = """You are a routing assistant for a content marketing tool.
Analyse the user's request and respond with ONLY a JSON object:
{
  "next_agent": "<first_agent>",
  "agent_chain": [],
  "topic": "<extracted topic>"
}

Agent names:
- "research"    → user wants facts or information about a topic
                  e.g. "research AI", "tell me about EVs"
- "blog"        → user wants a blog post or article written
                  e.g. "write a blog", "create an article"
- "linkedin"    → user wants a LinkedIn post
                  e.g. "linkedin post", "write for linkedin"
- "image"       → user wants an image created
                  e.g. "create an image", "generate a picture"
- "strategist"  → user wants a content strategy or calendar
                  e.g. "content strategy", "content plan"

CHAINING RULES — if the user wants multiple things in sequence,
set next_agent to the FIRST agent and agent_chain to the REST:

Examples of chained requests:
- "research X then write a blog" →
  {"next_agent":"research","agent_chain":["blog"],"topic":"X"}

- "research X and create a linkedin post" →
  {"next_agent":"research","agent_chain":["linkedin"],"topic":"X"}

- "research X then write a blog and linkedin post" →
  {"next_agent":"research","agent_chain":["blog","linkedin"],"topic":"X"}

- "write a blog about X then make a linkedin post" →
  {"next_agent":"blog","agent_chain":["linkedin"],"topic":"X"}

Single requests have empty agent_chain: []

Respond with ONLY the JSON. No explanation, no markdown."""


def query_handler_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    try:
        response = client.messages.create(
            model=config.claude_model,
            max_tokens=256,
            temperature=0.1,
            system=ROUTER_PROMPT,
            messages=[{"role": "user", "content": user_input}]
        )

        result = json.loads(response.content[0].text)

        return {
            **state,
            "next_agent":   result["next_agent"],
            "agent_chain":  result.get("agent_chain", []),
            "topic":        result["topic"],
            "error":        None
        }

    except Exception as e:
        return {
            **state,
            "next_agent":  "research",
            "agent_chain": [],
            "topic":       user_input,
            "error":       f"Routing error: {str(e)}"
        }