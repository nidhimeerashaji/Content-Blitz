import anthropic
from src.core.config import config
from src.workflow.state_management import AgentState

from src.core.config import load_config

def get_client():
    import anthropic
    return anthropic.Anthropic(api_key=load_config().anthropic_api_key)

LINKEDIN_PROMPT = """You are an expert LinkedIn content creator.
Write an engaging LinkedIn post that drives high engagement.

Your post must include:
- A strong opening line that stops the scroll (no "I am excited to...")
- Short punchy paragraphs (1-2 sentences max each)
- A personal insight or opinion on the topic
- A clear takeaway or lesson for the reader
- A question at the end to drive comments
- 5-7 relevant hashtags at the bottom

Target length: 150-300 words.
Tone: Authentic, professional, thought-provoking.
Do NOT use buzzwords like "synergy", "leverage", "game-changer"."""


def linkedin_writer_node(state: AgentState) -> AgentState:
    """
    Writes an engaging LinkedIn post about the topic.
    """
    topic = state["topic"]
    client = get_client()

    try:
        response = client.messages.create(
            model=config.claude_model,
            max_tokens=1024,       # LinkedIn posts are short
            temperature=0.8,       # creative and authentic tone
            system=LINKEDIN_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Write a LinkedIn post about: {topic}"
                }
            ]
        )

        linkedin_output = response.content[0].text

        return {
            **state,
            "linkedin_output": linkedin_output,
            "final_output": linkedin_output,
            "error": None
        }

    except Exception as e:
        error_msg = f"LinkedIn writer error: {str(e)}"
        return {
            **state,
            "linkedin_output": None,
            "final_output": f"Sorry, LinkedIn writing failed: {error_msg}",
            "error": error_msg
        }