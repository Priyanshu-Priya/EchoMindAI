"""
Telegram Bot Main Entry Point — Application builder.
"""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.core.config import settings
from bot.core.handlers import (
    start_command,
    help_command,
    fast_command,
    cancel_command,
    thought_command,
    resonance_command,
    handle_router_input,
    master_callback_handler
)
from bot.core.logger import log


async def post_init(application):
    """Set the standard Telegram bot menu commands so they appear in chat."""
    await application.bot.set_my_commands([
        ("thought", "Capture a fleeting thought: /thought <text>"),
        ("resonance", "Curate content: /resonance <url or title>"),
        ("fast", "Toggle instant save mode for Resonance"),
        ("cancel", "Discard current input"),
        ("help", "See usage guide"),
    ])


def main():
    """Build and run the bot application."""
    log.info("Starting EchoMindAiBot...")

    # Build the Application
    app = ApplicationBuilder().token(settings.telegram_bot_token).post_init(post_init).build()

    # Generic Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fast", fast_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("thought", thought_command))
    app.add_handler(CommandHandler("resonance", resonance_command))
    
    # Generic router (Resonance vs Thoughts detection)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_router_input))
    
    # Generic callback handler (parses domain specific callbacks)
    app.add_handler(CallbackQueryHandler(master_callback_handler))

    # Run the bot until Ctrl-C
    app.run_polling()


if __name__ == "__main__":
    main()
