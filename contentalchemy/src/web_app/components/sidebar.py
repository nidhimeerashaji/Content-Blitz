import streamlit as st

# ─── Example prompts grouped by type ───────────────────────
EXAMPLES = {
    "🔍 Research": [
        "Research the future of remote work",
        "Research AI trends in 2025",
        "Research electric vehicles market",
        "Research generative AI in healthcare",
    ],
    "✍️ Blog": [
        "Write a blog post about AI in healthcare",
        "Write a blog about climate change solutions",
        "Write a blog about productivity for founders",
        "Write a blog about the future of work",
    ],
    "💼 LinkedIn": [
        "LinkedIn post about leadership lessons",
        "LinkedIn post about remote work tips",
        "LinkedIn post about AI tools for marketers",
        "LinkedIn post about startup lessons learned",
    ],
    "🎨 Image": [
        "Create an image of a futuristic smart city",
        "Create an image of a modern coworking space",
        "Create an image of an AI robot working",
        "Create an image of a minimalist home office",
    ],
    "📊 Strategy": [
        "Content strategy for a SaaS startup",
        "Content plan for a personal finance brand",
        "Content calendar for a tech blog",
        "Content strategy for an e-commerce brand",
    ],
    "🔗 Chained": [
        "Research remote work trends then write a blog post",
        "Research AI in healthcare and create a LinkedIn post",
        "Write a blog about productivity then make a LinkedIn post",
        "Research EVs then write a blog and LinkedIn post",
    ],
}

# ─── CSS for badges ────────────────────────────────────────
BADGE_CSS = """
<style>
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
}
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid rgba(83,74,183,0.3);
    background: rgba(83,74,183,0.08);
    color: #534AB7;
    transition: all 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
}
.badge:hover {
    background: rgba(83,74,183,0.18);
    border-color: rgba(83,74,183,0.6);
}
@media(prefers-color-scheme: dark) {
    .badge {
        background: rgba(175,169,236,0.12);
        border-color: rgba(175,169,236,0.3);
        color: #AFA9EC;
    }
    .badge:hover {
        background: rgba(175,169,236,0.22);
    }
}
.section-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-color);
    opacity: 0.5;
    margin: 10px 0 4px 0;
}
</style>
"""


def render_sidebar():
    """Renders sidebar with clickable badge examples."""
    with st.sidebar:
        st.title("✨ ContentAlchemy")
        st.caption("Multi-agent AI content creation")

        st.divider()

        # Inject badge CSS
        st.markdown(BADGE_CSS, unsafe_allow_html=True)

        st.markdown("**💡 Quick examples** — click to use")

        # Render each category
        for category, prompts in EXAMPLES.items():
            st.markdown(
                f'<div class="section-label">{category}</div>',
                unsafe_allow_html=True
            )

            # Each prompt becomes a clickable button
            # We use st.button styled minimally
            for prompt in prompts:
                # Truncate label for display
                label = prompt if len(prompt) <= 35 else prompt[:32] + "..."

                if st.button(
                    label,
                    key=f"example_{prompt}",
                    use_container_width=True,
                    help=prompt   # full prompt shown on hover
                ):
                    # Inject into chat input via session state
                    st.session_state["prefilled_input"] = prompt
                    st.rerun()

        st.divider()

        # ─── Last request metadata ──────────────────────────
        if st.session_state.get("last_result"):
            result = st.session_state.last_result
            st.subheader("📊 Last request")

            agent = result.get("next_agent", "—")
            topic = result.get("topic", "—")
            error = result.get("error")

            AGENT_ICONS = {
                "research":   "🔍",
                "blog":       "✍️",
                "linkedin":   "💼",
                "image":      "🎨",
                "strategist": "📊",
            }
            icon = AGENT_ICONS.get(agent, "✨")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Agent", f"{icon} {agent.title()}")
            with col2:
                was_chained = (
                    result.get("research_output") and
                    (result.get("blog_output") or result.get("linkedin_output"))
                )
                st.metric("Chained", "Yes 🔗" if was_chained else "No")

            topic_display = topic[:28] + "..." if len(topic) > 28 else topic
            st.caption(f"Topic: {topic_display}")

            if error:
                st.error(f"Error: {error[:60]}")
            else:
                st.success("Completed ✅")

        st.divider()

        # ─── Clear conversation ─────────────────────────────
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_result = None
            st.session_state.pop("prefilled_input", None)
            st.rerun()

        # ─── Config info ────────────────────────────────────
        st.divider()
        from src.core.config import config
        st.caption(f"Model: `{config.claude_model}`")
        st.caption(f"Max tokens: `{config.max_tokens}`")