"""
Configuration — load and validate all environment variables.
"""

import os
import sys
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Supabase
    supabase_url: str
    supabase_key: str

    # Telegram
    telegram_bot_token: str

    # Groq
    groq_api_key: str

    # Security
    authorized_user_ids: list[str] = field(default_factory=list)


def _load_settings() -> Settings:
    """Load settings from environment, exit on missing required vars."""

    required = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    raw_ids = os.getenv("AUTHORIZED_USER_IDS", "")
    authorized = [uid.strip() for uid in raw_ids.split(",") if uid.strip()]

    return Settings(
        supabase_url=required["SUPABASE_URL"],
        supabase_key=required["SUPABASE_KEY"],
        telegram_bot_token=required["TELEGRAM_BOT_TOKEN"],
        groq_api_key=required["GROQ_API_KEY"],
        authorized_user_ids=authorized,
    )


settings = _load_settings()
