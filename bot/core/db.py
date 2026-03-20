"""
Core Database Module — initialize the Supabase client lazily.
"""

from supabase import create_client, Client
from bot.core.config import settings
from bot.core.logger import log

_supabase_client = None


def get_client() -> Client:
    """Lazy initialize the Supabase client to avoid timer crashes."""
    global _supabase_client
    if _supabase_client is None:
        log.info("Initializing Supabase client...")
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    return _supabase_client
