"""
Resonance Data Repository
"""

from bot.core.db import get_client
from bot.core.logger import log


def save_resonance_entry(data: dict) -> dict:
    """Save an entry to the Supabase resonance table."""
    client = get_client()

    payload = {
        "title": data["title"],
        "url": data.get("url", ""),
        "type": data["type"].lower(),
        "commentary": data.get("review", ""),
        "resonance_score": max(1, min(5, data.get("rating", 3))),
        "tags": data.get("tags", []),
    }

    log.info("Saving to Supabase 'resonance' table: %s", payload)

    result = client.table("resonance").insert(payload).execute()
    log.info("Saved! Response: %s", result)
    return result.data[0] if result.data else {}
