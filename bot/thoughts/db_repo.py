"""
Thoughts Database Repository
"""

from bot.core.db import get_client
from bot.core.logger import log


def save_thought_entry(data: dict) -> dict:
    """Save an entry to the Supabase thoughts table."""
    client = get_client()

    payload = {
        "content": data.get("content", ""),
        "mood": data.get("mood") or None,
        "is_published": data.get("is_published", False),
    }

    log.info("Saving to Supabase 'thoughts' table: %s", payload)

    result = client.table("thoughts").insert(payload).execute()
    log.info("Saved Thought! Response: %s", result)
    return result.data[0] if result.data else {}
