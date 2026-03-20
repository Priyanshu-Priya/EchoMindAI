"""
Authentication — restrict bot access to whitelisted users.
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.config import settings
from bot.core.logger import log


def is_authorized(user) -> bool:
    """Check if a Telegram user is in the authorized list.

    Supports matching by:
      - Numeric user ID (as string)
      - @username (case-insensitive)
    """
    if not settings.authorized_user_ids:
        return True  # no whitelist = allow all

    user_id_str = str(user.id)
    username = f"@{user.username}" if user.username else ""

    for allowed in settings.authorized_user_ids:
        if allowed.isdigit() and allowed == user_id_str:
            return True
        if allowed.startswith("@") and allowed.lower() == username.lower():
            return True

    return False


def authorized(func):
    """Decorator that rejects unauthorized users before running the handler."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_authorized(user):
            log.warning("Unauthorized access attempt: user_id=%s username=%s",
                        user.id if user else "?", user.username if user else "?")
            if update.effective_message:
                await update.effective_message.reply_text(
                    "⛔ *Unauthorized*\n\nYou are not authorized to use this bot.",
                    parse_mode="Markdown",
                )
            return
        return await func(update, context, *args, **kwargs)

    return wrapper
