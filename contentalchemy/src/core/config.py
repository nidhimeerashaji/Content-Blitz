import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """
    Tries Streamlit secrets first, falls back to .env
    """
    try:
        import streamlit as st
        val = st.secrets.get("api_keys", {}).get(key)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)


class AppConfig(BaseModel):
    anthropic_api_key:    str           = ""
    serp_api_key:         str           = ""
    openai_api_key:       Optional[str] = ""
    claude_model:         str           = "claude-sonnet-4-5"
    max_tokens:           int           = 4096
    temperature:          float         = 0.7
    max_research_results: int           = 10
    app_env:              str           = os.getenv("APP_ENV", "development")
    log_level:            str           = os.getenv("LOG_LEVEL", "INFO")

    def validate_keys(self) -> list[str]:
        missing = []
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.serp_api_key:
            missing.append("SERP_API_KEY")
        return missing


def load_config() -> AppConfig:
    return AppConfig(
        anthropic_api_key    = get_secret("ANTHROPIC_API_KEY"),
        serp_api_key         = get_secret("SERP_API_KEY"),
        openai_api_key       = get_secret("OPENAI_API_KEY"),
        max_tokens           = int(os.getenv("MAX_TOKENS", "4096")),
        max_research_results = int(os.getenv("MAX_RESEARCH_RESULTS", "10")),
    )


config = load_config()