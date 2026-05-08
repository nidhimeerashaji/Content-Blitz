import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

class AppConfig(BaseModel):
    # API keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    serp_api_key: str = os.getenv("SERP_API_KEY", "")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "")

    # Model settings
    claude_model: str = "claude-sonnet-4-5"
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    temperature: float = 0.7

    # Research settings
    max_research_results: int = int(os.getenv("MAX_RESEARCH_RESULTS", "10"))

    # App settings
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate_keys(self) -> list[str]:
        """Returns list of missing required keys."""
        missing = []
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.serp_api_key:
            missing.append("SERP_API_KEY")
        return missing

# Singleton config instance
config = AppConfig()

# Add to bottom of config.py
MAX_CONVERSATION_TURNS = 10  # keep last 10 exchanges in memory