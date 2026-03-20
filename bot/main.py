"""
Main — application entry point. Builds and runs the Telegram bot.
"""

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from bot.config import settings
from bot.handlers import (
    start_command,
    help_command,
    fast_command,
    cancel_command,
    handle_input,
    handle_callback,
)
from bot.logger import log


def main():
    """Build the bot application, register handlers, and start polling."""

    log.info("Starting Resonance Bot...")

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fast", fast_command))
    app.add_handler(CommandHandler("cancel", cancel_command))

    # Callback query handler  (inline keyboard buttons)
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Text message handler  (catch-all for content input)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    log.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
