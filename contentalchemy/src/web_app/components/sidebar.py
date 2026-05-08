import streamlit as st
from src.core.config import config

def render_sidebar():
    """Renders the sidebar with app info and last result details."""
    with st.sidebar:
        st.title("✨ ContentAlchemy")
        st.caption("Multi-agent AI content creation")

        st.divider()

        # Quick start examples
        st.subheader("💡 Try these")
        examples = [
            "Research the future of remote work",
            "Write a blog post about AI in healthcare",
            "LinkedIn post about leadership lessons",
            "Create a content strategy for a SaaS startup",
            "Research EVs then write a blog post about it",
            "Create an image of a futuristic office",
        ]
        for example in examples:
            st.code(example, language=None)

        st.divider()

        # Last result metadata
        if st.session_state.get("last_result"):
            result = st.session_state.last_result
            st.subheader("📊 Last request")

            agent = result.get("next_agent", "—")
            topic = result.get("topic", "—")
            error = result.get("error")

            st.metric("Agent used", agent.title())
            st.metric("Topic", topic[:30] + "..." if len(topic) > 30 else topic)

            if error:
                st.error(f"Error: {error}")
            else:
                st.success("Completed successfully")

            # Show chain if used
            chain = result.get("agent_chain", [])
            if result.get("research_output") and result.get("blog_output"):
                st.info("🔗 Research → Blog chain used")

        st.divider()

        # Clear conversation
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_result = None
            st.rerun()

        # Config info
        st.divider()
        st.caption(f"Model: {config.claude_model}")
        st.caption(f"Max tokens: {config.max_tokens}")