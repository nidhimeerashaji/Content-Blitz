import streamlit as st

AGENT_LABELS = {
    "research":   ("🔍", "Research Agent"),
    "blog":       ("✍️",  "Blog Writer"),
    "linkedin":   ("💼", "LinkedIn Writer"),
    "image":      ("🎨", "Image Generator"),
    "strategist": ("📊", "Content Strategist"),
}

def render_chat_message(role: str, content: str, agent: str = None):
    """Renders a single chat message with the correct avatar."""
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        # Pick avatar based on which agent responded
        icon = "✨"
        if agent and agent in AGENT_LABELS:
            icon = AGENT_LABELS[agent][0]

        with st.chat_message("assistant", avatar=icon):
            # Render as markdown so headings/bold/lists work
            st.markdown(content)