import anthropic
import requests
from src.core.config import config
from src.workflow.state_management import AgentState

# Anthropic client — reused across calls
client = anthropic.Anthropic(api_key=config.anthropic_api_key)

RESEARCH_PROMPT = """You are an expert research analyst.
You have been given a set of Google search results about a topic.
Your job is to synthesise these into a clear, well-structured research report.

The report should include:
- A brief overview of the topic (2-3 sentences)
- Key facts and findings (bullet points)
- Current trends and developments
- Important statistics or data points if available
- A short conclusion

Be factual, concise, and cite which result each point came from.
Format using clear headings and bullet points."""


def fetch_search_results(topic: str) -> list[dict]:
    """
    Calls SERP API to get Google search results for a topic.
    Returns a list of result dicts with title, snippet, link.
    """
    try:
        params = {
            "q": topic,
            "api_key": config.serp_api_key,
            "num": config.max_research_results,
            "engine": "google",
        }
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=10
        )
        data = response.json()

        # Extract organic results
        results = []
        for r in data.get("organic_results", []):
            results.append({
                "title":   r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link":    r.get("link", ""),
            })
        return results

    except Exception as e:
        # Return empty list on failure — Claude will still respond
        # with its training knowledge
        print(f"SERP API error: {e}")
        return []


def format_results_for_claude(results: list[dict]) -> str:
    """
    Turns the raw SERP results into a clean text block
    that Claude can easily read and reference.
    """
    if not results:
        return "No search results found. Use your training knowledge."

    formatted = ""
    for i, r in enumerate(results, 1):
        formatted += f"Result {i}: {r['title']}\n"
        formatted += f"URL: {r['link']}\n"
        formatted += f"Summary: {r['snippet']}\n\n"
    return formatted


def research_agent_node(state: AgentState) -> AgentState:
    """
    Main agent function — called by LangGraph.
    Fetches search results and asks Claude to synthesise them.
    """
    topic = state["topic"]

    try:
        # Step 1 — fetch real search results
        search_results = fetch_search_results(topic)

        # Step 2 — format them for Claude
        results_text = format_results_for_claude(search_results)

        # Step 3 — ask Claude to write the research report
        response = client.messages.create(
            model=config.claude_model,
            max_tokens=config.max_tokens,
            temperature=0.3,      # low temp = factual, accurate output
            system=RESEARCH_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Topic: {topic}\n\nSearch Results:\n{results_text}"
                }
            ]
        )

        research_output = response.content[0].text

        return {
            **state,
            "research_output": research_output,
            "final_output": research_output,
            "error": None
        }

    except Exception as e:
        error_msg = f"Research agent error: {str(e)}"
        return {
            **state,
            "research_output": None,
            "final_output": f"Sorry, research failed: {error_msg}",
            "error": error_msg
        }