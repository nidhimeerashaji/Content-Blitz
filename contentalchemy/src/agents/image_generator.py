import anthropic
import openai
from src.core.config import config
from src.workflow.state_management import AgentState

claude_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
openai_client = openai.OpenAI(api_key=config.openai_api_key)

PROMPT_OPTIMIZER = """You are an expert at writing DALL-E image generation prompts.
Convert the user's request into a detailed, optimised DALL-E 3 prompt.

A good prompt includes:
- Subject description (what/who is in the image)
- Style (photorealistic, illustration, minimalist, 3D render etc.)
- Lighting and mood
- Colour palette
- Composition details

Respond with ONLY the prompt text. No explanation."""


def image_generator_node(state: AgentState) -> AgentState:
    """
    Step 1 — Claude writes an optimised image prompt
    Step 2 — DALL-E 3 generates the image
    """
    topic = state["topic"]

    try:
        # Step 1 — Claude optimises the prompt
        prompt_response = claude_client.messages.create(
            model=config.claude_model,
            max_tokens=256,
            temperature=0.7,
            system=PROMPT_OPTIMIZER,
            messages=[
                {
                    "role": "user",
                    "content": f"Create an image prompt for: {topic}"
                }
            ]
        )
        optimised_prompt = prompt_response.content[0].text

        # Step 2 — DALL-E generates the image
        image_response = openai_client.images.generate(
            model="dall-e-3",
            prompt=optimised_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = image_response.data[0].url

        final_output = (
            f"**Generated Image**\n\n"
            f"**Optimised Prompt:** {optimised_prompt}\n\n"
            f"**Image URL:** {image_url}"
        )

        return {
            **state,
            "image_prompt": optimised_prompt,
            "final_output": final_output,
            "error": None
        }

    except Exception as e:
        error_msg = f"Image generation error: {str(e)}"
        return {
            **state,
            "image_prompt": None,
            "final_output": f"Sorry, image generation failed: {error_msg}",
            "error": error_msg
        }