"""Application configuration module following PEP 8 guidelines."""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Configuration settings for the Smart Retail application."""

    PROJECT_NAME: str = "Smart Retail & AI Batch Discount System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR}/sales.db"
    )

    # AI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "3.0"))
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "30"))
    PROMPT_VERSION: str = os.getenv("PROMPT_VERSION", "v1")

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "supersecretkey-for-smart-retail-system-dev-only"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


settings = Settings()
