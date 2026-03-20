"""
Formatter — render preview messages and star ratings.
"""


def stars_display(rating: int) -> str:
    """Convert numeric rating (1-5) to star emoji string."""
    filled = max(1, min(5, rating))
    return "⭐" * filled + "☆" * (5 - filled)


def format_preview(data: dict) -> str:
    """Render the review preview message for Telegram."""

    tags_str = " ".join(f"#{t}" for t in data.get("tags", [])) if data.get("tags") else "—"

    return (
        "📋 *Review Preview*\n"
        "─────────────────\n\n"
        f"📌 *Title:* {_escape_md(data.get('title', ''))}\n"
        f"📂 *Type:* {_escape_md(data.get('type', ''))}\n"
        f"💬 *Review:* {_escape_md(data.get('review', ''))}\n"
        f"⭐ *Rating:* {stars_display(data.get('rating', 3))}\n"
        f"🏷️ *Tags:* {_escape_md(tags_str)}\n\n"
        "Choose an action below:"
    )


def format_success(data: dict) -> str:
    """Render the confirmation message after saving."""
    return (
        "✅ *Saved to Resonance!*\n\n"
        f"📌 {_escape_md(data.get('title', ''))}\n"
        f"💬 {_escape_md(data.get('review', ''))}\n"
        f"⭐ {stars_display(data.get('rating', 3))}\n\n"
        "Your dashboard has been updated."
    )


def _escape_md(text: str) -> str:
    """Escape special Markdown V1 characters for Telegram."""
    if not text:
        return ""
    # In Markdown V1, we only need to escape _ * ` [
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text
