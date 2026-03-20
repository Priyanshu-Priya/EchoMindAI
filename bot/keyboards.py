"""
Keyboards — inline keyboard layouts for the review workflow.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def preview_keyboard() -> InlineKeyboardMarkup:
    """Main action buttons shown with the review preview."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm"),
            InlineKeyboardButton("✏️ Edit", callback_data="edit"),
        ],
        [
            InlineKeyboardButton("🔄 Regenerate", callback_data="regenerate"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ],
    ])


def edit_field_keyboard() -> InlineKeyboardMarkup:
    """Field selection for editing."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📌 Title", callback_data="edit_title"),
            InlineKeyboardButton("📂 Type", callback_data="edit_type"),
        ],
        [
            InlineKeyboardButton("💬 Review", callback_data="edit_review"),
            InlineKeyboardButton("⭐ Rating", callback_data="edit_rating"),
        ],
        [
            InlineKeyboardButton("↩️ Back", callback_data="back_to_preview"),
        ],
    ])


def type_selection_keyboard() -> InlineKeyboardMarkup:
    """Quick selection for content type."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📰 Article", callback_data="set_type_Article"),
            InlineKeyboardButton("📖 Book", callback_data="set_type_Book"),
        ],
        [
            InlineKeyboardButton("🎬 Video", callback_data="set_type_Video"),
            InlineKeyboardButton("🎙️ Podcast", callback_data="set_type_Podcast"),
        ],
        [
            InlineKeyboardButton("↩️ Back", callback_data="edit"),
        ],
    ])


def rating_keyboard() -> InlineKeyboardMarkup:
    """Star rating selection."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⭐ 1", callback_data="set_rating_1"),
            InlineKeyboardButton("⭐⭐ 2", callback_data="set_rating_2"),
            InlineKeyboardButton("⭐⭐⭐ 3", callback_data="set_rating_3"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="set_rating_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="set_rating_5"),
        ],
        [
            InlineKeyboardButton("↩️ Back", callback_data="edit"),
        ],
    ])
