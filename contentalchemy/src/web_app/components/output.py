import streamlit as st
import requests
from datetime import datetime

def render_output(result: dict):
    """
    Renders rich output based on which agent ran.
    Called after the chat message is shown.
    """
    agent = result.get("next_agent")

    if agent == "image":
        render_image_output(result)
    elif agent == "blog":
        render_blog_output(result)
    elif agent == "research":
        render_research_output(result)
    elif agent == "linkedin":
        render_linkedin_output(result)


def render_image_output(result: dict):
    """Shows the generated image inline."""
    final_output = result.get("final_output", "")

    # Extract URL from final_output string
    url = None
    for line in final_output.split("\n"):
        if "Image URL:" in line:
            url = line.split("Image URL:")[-1].strip()
            break

    if url:
        st.divider()
        st.subheader("🎨 Generated Image")
        try:
            st.image(url, use_column_width=True)
            st.caption(f"Prompt: {result.get('image_prompt', '')}")

            # Download button
            img_data = requests.get(url).content
            st.download_button(
                label="⬇️ Download Image",
                data=img_data,
                file_name=f"contentalchemy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
        except Exception as e:
            st.warning(f"Could not load image: {e}. Open the URL directly.")
            st.code(url)


def render_blog_output(result: dict):
    """Shows a download button for the blog post."""
    blog_output = result.get("blog_output")
    if not blog_output:
        return

    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.download_button(
            label="⬇️ Download Blog Post (.md)",
            data=blog_output,
            file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

    with col2:
        # Show research was used if available
        if result.get("research_output"):
            st.success("✅ Written using live research data")


def render_research_output(result: dict):
    """Shows a download button for the research report."""
    research_output = result.get("research_output")
    if not research_output:
        return

    st.divider()
    st.download_button(
        label="⬇️ Download Research Report (.md)",
        data=research_output,
        file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


def render_linkedin_output(result: dict):
    """Shows a copy-friendly box for the LinkedIn post."""
    linkedin_output = result.get("linkedin_output")
    if not linkedin_output:
        return

    st.divider()
    st.subheader("💼 Ready to post on LinkedIn")
    st.text_area(
        label="Copy this to LinkedIn:",
        value=linkedin_output,
        height=300,
        help="Select all text, copy, then paste directly into LinkedIn"
    )