"""
Database — Supabase client for saving resonance entries.
Uses lazy initialization to avoid import-time errors.
"""

from supabase import create_client, Client

from bot.config import settings
from bot.logger import log

_client: Client | None = None


def _get_client() -> Client:
    """Lazily initialize and return the Supabase client."""
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_key)
        log.info("Supabase client initialized.")
    return _client


async def save_resonance_entry(data: dict) -> dict:
    """Save a confirmed review entry to the Supabase 'resonance' table.

    Maps bot fields to database schema:
      - review   → commentary
      - rating   → resonance_score (×20, so 1-5 becomes 20-100)
      - tags     → tags (text[])

    Returns the inserted row or raises on failure.
    """
    row = {
        "title": data["title"],
        "url": data.get("url", ""),
        "type": data["type"].lower(),
        "commentary": data.get("review", ""),
        "resonance_score": max(1, min(5, data.get("rating", 3))),
        "tags": data.get("tags", []),
    }

    log.info("Saving to Supabase: %s", row["title"])

    try:
        client = _get_client()
        result = client.table("resonance").insert(row).execute()
        log.info("Saved successfully — id: %s", result.data[0]["id"] if result.data else "?")
        return result.data[0] if result.data else {}
    except Exception as e:
        log.error("Supabase insert failed: %s", e)
        raise
