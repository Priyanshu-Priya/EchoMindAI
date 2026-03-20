"""
Core Handlers — Generic commands and entry point router.
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from bot.core.auth import authorized
from bot.core.session import get_session, clear_session
from bot.resonance.content_detector import extract_url, detect_content_type

# ─── Command Handlers ────────────────────────────────────────────────

@authorized
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — welcome message."""
    await update.message.reply_text(
        "👋 *Welcome to the Dashboard Automation Bot!*\n\n"
        "Send me a URL or plain text, and I'll route it automatically. Or use explicit commands:\n\n"
        "*Commands:*\n"
        "💭 `/thought <text>` — Instantly save a fleeting observation\n"
        "🧠 `/resonance <link/title>` — Instantly curate a piece of content\n"
        "⚡ `/fast` — Toggle instant saving (skip previews)\n"
        "❌ `/cancel` — Clear the current operation\n"
        "📖 `/help` — Detailed guide",
        parse_mode="Markdown",
    )

@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help — detailed usage guide."""
    await update.message.reply_text(
        "📖 *How to use*\n\n"
        "*1. Auto-Routing*\n"
        "Just send any text. If it looks like a URL, I'll process it as Resonance. If it's plain text, I'll ask you to choose between Resonance and Thought.\n\n"
        "*2. Explicit Commands (Faster!)*\n"
        "• `/thought Just realized modular code is great` → Jumps straight to Mood selection.\n"
        "• `/resonance Sapiens` → Forces the AI to review it without asking questions.\n\n"
        "*3. Fast Mode*\n"
        "• `/fast` → When enabled, Resonance URLs are saved instantly without asking for confirmation.\n\n"
        "*4. Emergency*\n"
        "• `/cancel` → Stuck in a menu? This clears everything.",
        parse_mode="Markdown",
    )

@authorized
async def thought_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /thought — explicit workflow."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    text = " ".join(context.args).strip()
    
    if not text:
        await update.message.reply_text("💡 Please provide the thought text. Example:\n`/thought Code modularity is essential.`", parse_mode="Markdown")
        return

    session.domain = "thought"
    session.state = "selecting_mood"
    session.data = {"content": text, "mood": "", "is_published": False}
    
    from bot.thoughts.keyboards import mood_keyboard
    await update.message.reply_text(
        f"*{text}*\n\nWhat's your mood for this thought?",
        parse_mode="Markdown",
        reply_markup=mood_keyboard()
    )

@authorized
async def resonance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resonance — explicit workflow."""
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("💡 Please provide content. Example:\n`/resonance Sapiens by Yuval Noah Harari`", parse_mode="Markdown")
        return
        
    from bot.resonance.handlers import process_new_resonance
    await process_new_resonance(update, context, text)

@authorized
async def fast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fast — toggle fast mode."""
    session = get_session(update.effective_user.id)
    session.fast_mode = not session.fast_mode
    status = "ON ⚡" if session.fast_mode else "OFF 🐢"
    await update.message.reply_text(f"🔀 Fast mode is now *{status}*", parse_mode="Markdown")

@authorized
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel — discard current operation."""
    user_id = update.effective_user.id
    clear_session(user_id)
    await update.message.reply_text("❌ Operation cancelled. Session cleared.")


# ─── Router ──────────────────────────────────────────────────────────

@authorized
async def handle_router_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route text to Resonance or Thought workflows based on content."""
    text = update.message.text.strip()
    user_id = update.effective_user.id
    session = get_session(user_id)

    # 1. If currently inside a session state (e.g., editing resonance or setting custom mood)
    if session.state != "idle":
        if hasattr(session, "domain") and session.domain == "thought":
            # Handled by thought logic via direct pass - wait, we should dispatch it
            from bot.thoughts.handlers import process_thought_text_input
            await process_thought_text_input(update, context)
            return
        elif session.state == "editing_field":
            # Handled by resonance logic
            from bot.resonance.handlers import process_resonance_edit_input
            await process_resonance_edit_input(update, context, session, text)
            return
        else:
            await update.message.reply_text("⚠️ Please finish or /cancel your current pending item first.")
            return

    # 2. Check heuristically if it's Resonance or Thought
    url = extract_url(text)
    detected = detect_content_type(text, url)

    if url or detected:
        # Straight to Resonance
        from bot.resonance.handlers import process_new_resonance
        await process_new_resonance(update, context, text)
    else:
        # Plain text without obvious markers — ask the user
        session.temp_text = text
        session.domain = "routing"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🧠 Content Link", callback_data="route_resonance"),
                InlineKeyboardButton("📚 Book", callback_data="route_resonance_book")
            ],
            [
                InlineKeyboardButton("💭 Thought (Observation)", callback_data="route_thought")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])
        
        await update.message.reply_text(
            "What kind of entry is this?",
            reply_markup=keyboard
        )


@authorized
async def master_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Root callback router separating Resonance, Thoughts, and common actions."""
    query = update.callback_query
    await query.answer()

    data_str = query.data
    user_id = update.effective_user.id
    session = get_session(user_id)

    # 1. Handle common actions
    if data_str == "cancel":
        clear_session(user_id)
        await query.edit_message_text("❌ Cancelled. Entry discarded.")
        return

    # 2. Routing selection
    if data_str.startswith("route_resonance"):
        from bot.resonance.handlers import process_new_resonance
        # clear the routing state from session and force into Resonance
        text = session.temp_text
        force_type = "book" if data_str == "route_resonance_book" else None
        
        clear_session(user_id)
        # Re-mock the text for process_new_resonance
        await query.edit_message_text("🔍 Analyzing as Resonance content...")
        await process_new_resonance(update, context, text, edit_message=query.message, force_type=force_type)
        return

    # 3. Route to specific domains
    # Try thoughts first (since it has specific prefixes: mood_, vis_, thought_, route_thought)
    if data_str.startswith(("mood_", "vis_", "thought_", "route_thought")):
        from bot.thoughts.handlers import handle_thought_callbacks
        handled = await handle_thought_callbacks(update, context)
        if handled:
            return

    # Fallback entirely to Resonance
    from bot.resonance.handlers import handle_callback as resonance_callbacks
    await resonance_callbacks(update, context)


