# ✨ ContentAlchemy

> AI-powered multi-agent content creation — research, blogs, LinkedIn posts, images and strategy — all from a single chat interface.

---

## What is ContentAlchemy?

ContentAlchemy is a multi-agent AI system built with LangGraph and Claude Sonnet. You describe what content you need in plain English — the system figures out which specialist agent to call, runs it, and delivers high-quality output in seconds.

It supports single requests and chained workflows — so you can say *"research AI trends then write a blog post about it"* and two agents run automatically in sequence, the second one using the first one's output as context.

---

## Demo

```
You:  Research the future of remote work then write a blog post about it

✨ ContentAlchemy:
  🔍 Research Agent    → fetches live Google results, synthesises report
  ✍️  Blog Writer Agent → writes SEO blog using the research as context
  
  # The Future of Remote Work: What the Data Shows
  ...800-1200 word SEO blog with real facts from the research...
```

---

## Agents

| Agent | Trigger | What it does |
|---|---|---|
| 🔍 Research | "research X", "tell me about X" | Google search via SERP API + Claude synthesis |
| ✍️ Blog Writer | "write a blog about X" | SEO-optimised long-form blog post in markdown |
| 💼 LinkedIn Writer | "linkedin post about X" | Short punchy post with hashtags |
| 🎨 Image Generator | "create an image of X" | Claude writes prompt → DALL-E 3 generates image |
| 📊 Content Strategist | "content strategy for X" | 4-week content calendar with KPIs |

---

## Agent Chaining

Agents can be chained together in a single message:

```
"Research X then write a blog"           → Research → Blog
"Research X and create a linkedin post"  → Research → LinkedIn
"Write a blog about X then make a       → Blog → LinkedIn
 linkedin post"
"Research X, write a blog, then         → Research → Blog → LinkedIn
 make a linkedin post"
```

When chained, each agent's output is passed as context to the next — so the blog post contains real facts from the research report.

---

## Tech Stack

| Component | Technology |
|---|---|
| Multi-agent orchestration | LangGraph |
| Primary LLM | Anthropic Claude Sonnet |
| Web research | SERP API |
| Image generation | OpenAI DALL-E 3 |
| Web interface | Streamlit |
| Data validation | Pydantic |
| Secret management | python-dotenv |

---

## Project Structure

```
contentalchemy/
├── src/
│   ├── agents/
│   │   ├── query_handler.py       ← routes requests to correct agent
│   │   ├── research_agent.py      ← SERP API + Claude research
│   │   ├── blog_writer.py         ← SEO blog generation
│   │   ├── linkedin_writer.py     ← LinkedIn post generation
│   │   ├── image_generator.py     ← Claude prompt + DALL-E 3
│   │   └── content_strategist.py  ← content strategy + calendar
│   ├── core/
│   │   └── config.py              ← centralised configuration
│   ├── workflow/
│   │   ├── state_management.py    ← LangGraph AgentState definition
│   │   └── langgraph_workflow.py  ← graph, routing, chain logic
│   ├── web_app/
│   │   ├── streamlit_app.py       ← main Streamlit app
│   │   └── components/
│   │       ├── sidebar.py         ← sidebar with examples
│   │       ├── chat.py            ← chat message rendering
│   │       └── output.py          ← image/download rendering
│   └── utils/
│       └── content_optimization.py
├── tests/
│   ├── test_phase2.py             ← routing tests
│   ├── test_phase3.py             ← agent tests
│   └── test_phase4.py             ← chaining tests
├── .env.example                   ← API key template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd contentalchemy

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
ANTHROPIC_API_KEY=sk-ant-...      # console.anthropic.com
SERP_API_KEY=...                  # serpapi.com (100 free searches/month)
OPENAI_API_KEY=sk-...             # platform.openai.com (for DALL-E 3)
```

### 4. Run the app

```bash
PYTHONPATH=. streamlit run src/web_app/streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Running Tests

```bash
# Test routing (Phase 2)
python test_phase2.py

# Test all agents (Phase 3)
python test_phase3.py

# Test agent chaining (Phase 4)
python test_phase4.py
```

---

## Example Prompts

**Single agent:**
```
Research the latest trends in generative AI
Write a blog post about climate change solutions
Create a LinkedIn post about leadership lessons
Generate an image of a futuristic smart city
Build a content strategy for a SaaS startup
```

**Chained workflows:**
```
Research remote work trends then write a blog post about it
Research AI in healthcare and create a LinkedIn post
Write a blog about productivity then make a LinkedIn post from it
Research EVs, write a blog, then create a LinkedIn post
```

---

## How It Works

```
User message
    ↓
Query Handler Agent (Claude)
    classifies intent → sets next_agent + agent_chain
    ↓
First Agent runs
    reads state["topic"] → calls API → writes to state
    ↓
chain_router checks agent_chain
    ├── more agents? → pop_chain → next agent
    └── empty?       → END
    ↓
Final state returned
    final_output shown in chat UI
```

State is shared across all agents via LangGraph's `AgentState` TypedDict. Each agent reads from state (topic, previous outputs) and writes back to it (its own output + final_output). This is how the blog writer knows to use the research report — it checks `state["research_output"]` before deciding which prompt to use.

---

## API Keys

| Key | Where to get it | Free tier |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | $5 free credit |
| `SERP_API_KEY` | [serpapi.com](https://serpapi.com) | 100 searches/month |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Pay per use |

> OpenAI key is optional — only needed for image generation. All other agents use Claude exclusively.

---

## Configuration

All settings live in `src/core/config.py` and are read from `.env`:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required |
| `SERP_API_KEY` | — | Required for research |
| `OPENAI_API_KEY` | — | Optional, for images |
| `MAX_TOKENS` | 4096 | Max Claude response length |
| `MAX_RESEARCH_RESULTS` | 10 | Google results per query |
| `APP_ENV` | development | development / production |
| `LOG_LEVEL` | INFO | DEBUG / INFO / WARNING |

---

## Built With

- [LangGraph](https://github.com/langchain-ai/langgraph) — multi-agent orchestration
- [Anthropic Claude](https://anthropic.com) — language model
- [SERP API](https://serpapi.com) — Google search
- [OpenAI DALL-E 3](https://openai.com) — image generation
- [Streamlit](https://streamlit.io) — web interface

---

## License

MIT