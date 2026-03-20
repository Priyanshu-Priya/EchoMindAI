"""
Thoughts Keyboards — Mood selection and Visibility toggles.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MOODS = [
    ("🚀 Productive", "Productive"),
    ("💭 Pensive", "Pensive"),
    ("⚡ Excited", "Excited"),
    ("🤯 Frustrated", "Frustrated"),
    ("🌊 Calm", "Calm"),
    ("🤔 Curious", "Curious"),
    ("🙏 Grateful", "Grateful"),
    ("😴 Tired", "Tired")
]

def mood_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting a mood."""
    buttons = []
    # 2 columns per row
    row = []
    for label, val in MOODS:
        row.append(InlineKeyboardButton(label, callback_data=f"mood_{val}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    # Add custom and no mood buttons
    buttons.append([
        InlineKeyboardButton("✍️ Custom", callback_data="mood_custom"),
        InlineKeyboardButton("➖ Skip Mood", callback_data="mood_none")
    ])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)

def visibility_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting visibility (published flag)."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Publish immediately", callback_data="vis_public")],
        [InlineKeyboardButton("🔒 Keep Private", callback_data="vis_private")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

def thought_preview_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for final confirmation."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Post Thought", callback_data="thought_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])
