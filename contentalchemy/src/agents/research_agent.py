import anthropic
import requests
from src.core.config import load_config
from src.workflow.state_management import AgentState

# load fresh config — picks up Streamlit secrets
config = load_config()

RESEARCH_PROMPT = """You are an expert research analyst.
You have been given a set of Google search results about a topic.
Synthesise these into a clear, well-structured research report with:
- A brief overview (2-3 sentences)
- Key facts and findings (bullet points)
- Current trends and developments
- Important statistics or data points
- A short conclusion
Be factual and cite which result each point came from."""


def get_client():
    """Returns fresh Anthropic client using latest config."""
    cfg = load_config()
    return anthropic.Anthropic(api_key=cfg.anthropic_api_key)


def fetch_search_results(topic: str) -> list[dict]:
    cfg = load_config()
    try:
        params = {
            "q":       topic,
            "api_key": cfg.serp_api_key,
            "num":     cfg.max_research_results,
            "engine":  "google",
        }
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=10
        )
        data = response.json()
        results = []
        for r in data.get("organic_results", []):
            results.append({
                "title":   r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link":    r.get("link", ""),
            })
        return results
    except Exception as e:
        print(f"SERP API error: {e}")
        return []


def format_results_for_claude(results: list[dict]) -> str:
    if not results:
        return "No search results found. Use your training knowledge."
    formatted = ""
    for i, r in enumerate(results, 1):
        formatted += f"Result {i}: {r['title']}\n"
        formatted += f"URL: {r['link']}\n"
        formatted += f"Summary: {r['snippet']}\n\n"
    return formatted


def research_agent_node(state: AgentState) -> AgentState:
    topic  = state["topic"]
    client = get_client()
    cfg    = load_config()

    try:
        search_results = fetch_search_results(topic)
        results_text   = format_results_for_claude(search_results)

        response = client.messages.create(
            model=cfg.claude_model,
            max_tokens=cfg.max_tokens,
            temperature=0.3,
            system=RESEARCH_PROMPT,
            messages=[{
                "role":    "user",
                "content": f"Topic: {topic}\n\nSearch Results:\n{results_text}"
            }]
        )

        research_output = response.content[0].text
        return {
            **state,
            "research_output": research_output,
            "final_output":    research_output,
            "error":           None
        }

    except Exception as e:
        error_msg = f"Research agent error: {str(e)}"
        return {
            **state,
            "research_output": None,
            "final_output":    f"Sorry, research failed: {error_msg}",
            "error":           error_msg
        }