import anthropic
from src.core.config import config
from src.workflow.state_management import AgentState

client = anthropic.Anthropic(api_key=config.anthropic_api_key)

BLOG_PROMPT = """You are an expert SEO blog writer.
Write a comprehensive, engaging, SEO-optimised blog post.

Your blog post must include:
- A compelling H1 title with the main keyword
- An engaging introduction that hooks the reader (first 2 sentences must grab attention)
- At least 4 sections with H2 subheadings
- Bullet points and numbered lists where appropriate
- A conclusion with a clear call to action
- Keywords placed naturally throughout (never keyword stuffed)
- Meta description at the very end (150-160 characters, labelled "Meta Description:")

Target length: 800-1200 words.
Tone: Professional but conversational — write like a smart friend, not a textbook.
Format: Markdown."""

BLOG_WITH_RESEARCH_PROMPT = """You are an expert SEO blog writer.
You have been given research notes to base your blog post on.
Write a comprehensive, engaging, SEO-optimised blog post using the research provided.

Your blog post must include:
- A compelling H1 title with the main keyword
- An engaging introduction that hooks the reader
- At least 4 sections with H2 subheadings using insights from the research
- Bullet points and numbered lists where appropriate
- Specific facts, statistics and findings from the research
- A conclusion with a clear call to action
- Meta description at the very end (150-160 characters, labelled "Meta Description:")

Target length: 800-1200 words.
Tone: Professional but conversational.
Format: Markdown.
Important: Use the research to make the blog factual and credible."""


def blog_writer_node(state: AgentState) -> AgentState:
    topic = state["topic"]
    research_output = state.get("research_output")

    try:
        # Choose prompt and message based on whether research exists
        if research_output:
            system_prompt = BLOG_WITH_RESEARCH_PROMPT
            user_message = (
                f"Topic: {topic}\n\n"
                f"Research Notes:\n{research_output}\n\n"
                f"Now write the blog post using this research."
            )
        else:
            system_prompt = BLOG_PROMPT
            user_message = f"Write a blog post about: {topic}"

        response = client.messages.create(
            model=config.claude_model,
            max_tokens=config.max_tokens,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        blog_output = response.content[0].text

        return {
            **state,
            "blog_output":  blog_output,
            "final_output": blog_output,
            "error":        None
        }

    except Exception as e:
        error_msg = f"Blog writer error: {str(e)}"
        return {
            **state,
            "blog_output":  None,
            "final_output": f"Sorry, blog writing failed: {error_msg}",
            "error":        error_msg
        }