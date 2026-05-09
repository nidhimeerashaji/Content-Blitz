import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.core.config import config, load_config
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

# ─── Reload config using Streamlit secrets ───────────────────
# config is loaded at module level in config.py
# but Streamlit secrets aren't available until the app runs
# so we reload here to pick them up
cfg = load_config()

# ─── Validate API keys on startup ───────────────────────────
missing_keys = cfg.validate_keys()
if missing_keys:
    st.error(f"⚠️ Missing API keys: {', '.join(missing_keys)}")
    st.info(
        "Add your keys to `.streamlit/secrets.toml`:\n\n"
        "```toml\n"
        "[api_keys]\n"
        "ANTHROPIC_API_KEY = 'sk-ant-...'\n"
        "SERP_API_KEY      = 'your-key'\n"
        "OPENAI_API_KEY    = 'sk-...'\n"
        "```"
    )
    st.stop()   # stops the app here if keys are missing

# ─── Session state init ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ─── Layout ─────────────────────────────────────────────────
render_sidebar()

st.title("✨ ContentAlchemy")
st.caption("AI-powered content creation — research, blogs, LinkedIn, images & strategy")

st.divider()

# ─── Chat history ────────────────────────────────────────────
for message in st.session_state.messages:
    render_chat_message(
        message["role"],
        message["content"],
        message.get("agent")
    )

# ─── Chat input ──────────────────────────────────────────────
user_input = st.chat_input(
    "What content do you need? e.g. 'Write a blog about AI trends' "
    "or 'Research remote work then write a LinkedIn post'"
)

if user_input:
    # Show user message immediately
    render_chat_message("user", user_input)
    st.session_state.messages.append({
        "role":    "user",
        "content": user_input
    })

    with st.spinner("✨ Creating your content..."):
        try:
            # Rebuild clients with fresh config from secrets
            import anthropic
            import openai as openai_lib

            # Pass fresh keys into workflow via environment
            # so all agents pick up Streamlit secrets
            os.environ["ANTHROPIC_API_KEY"] = cfg.anthropic_api_key
            os.environ["SERP_API_KEY"]      = cfg.serp_api_key
            os.environ["OPENAI_API_KEY"]    = cfg.openai_api_key or ""

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

            response = f"⚠️ {error}\n\n{final_output}" if error else final_output

            # Show assistant message
            render_chat_message("assistant", response, agent_used)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": response,
                "agent":   agent_used,
                "result":  result
            })

            # Render rich output (images, downloads)
            render_output(result)

        except Exception as e:
            error_msg = f"Something went wrong: {str(e)}"
            render_chat_message("assistant", f"⚠️ {error_msg}")
            st.session_state.messages.append({
                "role":    "assistant",
                "content": error_msg
            })

    st.rerun()