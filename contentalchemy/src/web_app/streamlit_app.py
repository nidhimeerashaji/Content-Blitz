import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.core.config import config
from src.workflow.langgraph_workflow import workflow
from src.web_app.components.sidebar import render_sidebar
from src.web_app.components.chat import render_chat_message
from src.web_app.components.output import render_output

# ─── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="ContentAlchemy",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Validate API keys on startup ───────────────────────────
missing_keys = config.validate_keys()
if missing_keys:
    st.error(f"⚠️ Missing API keys: {', '.join(missing_keys)}")
    st.info(
        "Add your keys to `.env`:\n\n"
        "```\n"
        "ANTHROPIC_API_KEY=sk-ant-...\n"
        "SERP_API_KEY=your-key\n"
        "OPENAI_API_KEY=sk-...\n"
        "```"
    )
    st.stop()

# ─── Session state init ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# prefilled_input is set by sidebar badge clicks
if "prefilled_input" not in st.session_state:
    st.session_state.prefilled_input = ""

# ─── Sidebar ────────────────────────────────────────────────
render_sidebar()

# ─── Header ─────────────────────────────────────────────────
st.title("✨ ContentAlchemy")
st.caption(
    "Multi-agent AI content — research, blogs, LinkedIn, images & strategy. "
    "Try chaining: *'Research AI trends then write a blog post'*"
)

st.divider()

# ─── Chat history ────────────────────────────────────────────
for message in st.session_state.messages:
    render_chat_message(
        message["role"],
        message["content"],
        message.get("agent")
    )

# ─── Handle prefilled input from sidebar badge click ─────────
# When a badge is clicked, prefilled_input is set and we rerun.
# We then immediately process that input as if the user typed it.
prefilled = st.session_state.get("prefilled_input", "")

if prefilled:
    # Clear it so it doesn't loop
    st.session_state["prefilled_input"] = ""
    user_input = prefilled
    auto_submit = True
else:
    user_input = st.chat_input(
        "What content do you need? e.g. 'Write a blog about AI trends' "
        "or 'Research remote work then write a LinkedIn post about it'"
    )
    auto_submit = False

# ─── Process input ───────────────────────────────────────────
if user_input:
    # Show user message
    render_chat_message("user", user_input)
    st.session_state.messages.append({
        "role":    "user",
        "content": user_input
    })

    with st.spinner("✨ Creating your content..."):
        try:
            result = workflow.invoke({
                "messages":        st.session_state.messages,
                "user_input":      user_input,
                "next_agent":      "",
                "agent_chain":     [],
                "current_agent":   None,
                "topic":           "",
                "research_output": None,
                "blog_output":     None,
                "linkedin_output": None,
                "image_prompt":    None,
                "final_output":    None,
                "error":           None,
            })

            st.session_state.last_result = result

            agent_used   = result["next_agent"]
            final_output = result["final_output"]
            error        = result.get("error")

            response = (
                f"⚠️ {error}\n\n{final_output}" if error else final_output
            )

            # Show assistant message
            render_chat_message("assistant", response, agent_used)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": response,
                "agent":   agent_used,
                "result":  result
            })

            # Render rich output (images, downloads, copy boxes)
            render_output(result)

        except Exception as e:
            error_msg = f"Something went wrong: {str(e)}"
            render_chat_message("assistant", f"⚠️ {error_msg}")
            st.session_state.messages.append({
                "role":    "assistant",
                "content": error_msg
            })

    st.rerun()