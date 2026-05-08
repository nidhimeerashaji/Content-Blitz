import streamlit as st
from src.workflow.langgraph_workflow import workflow
from src.web_app.components.sidebar import render_sidebar
from src.web_app.components.chat import render_chat_message
from src.web_app.components.output import render_output

# ─── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="ContentAlchemy",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Session state init ─────────────────────────────────────
# Streamlit re-runs the entire script on every interaction
# session_state persists data across those re-runs
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# ─── Layout ────────────────────────────────────────────────
render_sidebar()

st.title("✨ ContentAlchemy")
st.caption("AI-powered content creation — research, blog, LinkedIn, images & strategy")

st.divider()

# ─── Chat history ───────────────────────────────────────────
for message in st.session_state.messages:
    render_chat_message(message["role"], message["content"])

# ─── Chat input ────────────────────────────────────────────
user_input = st.chat_input(
    "What content do you need? e.g. 'Write a blog about AI trends' or "
    "'Research remote work then write a LinkedIn post'"
)

if user_input:
    # Show user message immediately
    render_chat_message("user", user_input)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Run the workflow
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

            # Store result for sidebar display
            st.session_state.last_result = result

            # Build assistant response
            agent_used = result["next_agent"]
            final_output = result["final_output"]
            error = result.get("error")

            if error:
                response = f"⚠️ {error}\n\n{final_output}"
            else:
                response = final_output

            # Show assistant response
            render_chat_message("assistant", response)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": response,
                "agent":   agent_used,
                "result":  result
            })

            # Render rich output (images, formatted content)
            render_output(result)

        except Exception as e:
            error_msg = f"Something went wrong: {str(e)}"
            render_chat_message("assistant", f"⚠️ {error_msg}")
            st.session_state.messages.append({
                "role":    "assistant",
                "content": error_msg
            })

    st.rerun()