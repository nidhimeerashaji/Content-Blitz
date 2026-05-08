import anthropic
from src.core.config import config
from src.workflow.state_management import AgentState

client = anthropic.Anthropic(api_key=config.anthropic_api_key)

STRATEGIST_PROMPT = """You are an expert content marketing strategist.
Create a comprehensive content strategy and calendar.

Your strategy must include:
- Executive summary of the content approach
- Target audience definition
- Content pillars (3-4 main themes)
- 4-week content calendar with:
  * Blog post ideas (1 per week)
  * LinkedIn posts (3 per week)
  * Content repurposing opportunities
- KPIs to measure success
- Quick wins (content that can be created immediately)

Format everything clearly with headings, tables where helpful,
and actionable recommendations."""


def content_strategist_node(state: AgentState) -> AgentState:
    """
    Creates a full content strategy and calendar for the topic.
    """
    topic = state["topic"]

    try:
        response = client.messages.create(
            model=config.claude_model,
            max_tokens=config.max_tokens,
            temperature=0.6,
            system=STRATEGIST_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Create a content strategy for: {topic}"
                }
            ]
        )

        strategist_output = response.content[0].text

        return {
            **state,
            "final_output": strategist_output,
            "error": None
        }

    except Exception as e:
        error_msg = f"Strategist error: {str(e)}"
        return {
            **state,
            "final_output": f"Sorry, strategy creation failed: {error_msg}",
            "error": error_msg
        }