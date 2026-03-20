"""
Thoughts Formatter
"""

def _bool_icon(val: bool) -> str:
    return "🌍 Public" if val else "🔒 Private"


def thought_preview(data: dict) -> str:
    """Render the preview payload for a thought."""
    mood_display = data.get("mood", "")
    mood_text = f"Mood: {mood_display}\n" if mood_display else ""
    return (
        "💭 *New Thought Preview*\n"
        "────────────────────\n\n"
        f"*{data.get('content', '')}*\n\n"
        f"{mood_text}"
        f"Visibility: {_bool_icon(data.get('is_published', False))}\n\n"
        "Choose an action below:"
    )

def thought_success(data: dict) -> str:
    """Render the final success message."""
    mood_display = data.get("mood", "")
    mood_text = f"Mood: {mood_display}\n" if mood_display else ""
    return (
        "✅ *Thought Saved!*\n\n"
        f"_{data.get('content', '')}_\n\n"
        f"{mood_text}"
        f"Visibility: {_bool_icon(data.get('is_published', False))}"
    )
