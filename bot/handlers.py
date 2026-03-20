"""
Handlers — Telegram command and message handlers for the review workflow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from bot.auth import authorized
from bot.session import get_session, clear_session, set_session_data
from bot.content_detector import extract_url, detect_content_type, fetch_url_metadata
from bot.ai_engine import generate_review
from bot.database import save_resonance_entry
from bot.formatter import format_preview, format_success
from bot.keyboards import (
    preview_keyboard,
    edit_field_keyboard,
    type_selection_keyboard,
    rating_keyboard,
)
from bot.logger import log


# ─── Command Handlers ────────────────────────────────────────────────


@authorized
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — welcome message."""
    await update.message.reply_text(
        "👋 *Welcome to Resonance Bot!*\n\n"
        "I'm your AI-powered content curator. Send me:\n\n"
        "• A *URL* (YouTube, article, blog, podcast)\n"
        "• A *book name* (e.g., _Sapiens by Yuval Noah Harari_)\n"
        "• A *podcast title* or *video name*\n\n"
        "I'll generate a sharp, curated review for your Resonance dashboard.\n\n"
        "*Commands:*\n"
        "/start — This message\n"
        "/help — Detailed usage guide\n"
        "/fast — Toggle fast mode (skip preview)\n"
        "/cancel — Cancel current operation",
        parse_mode="Markdown",
    )


@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help — detailed usage guide."""
    await update.message.reply_text(
        "📖 *How to use Resonance Bot*\n"
        "─────────────────\n\n"
        "*1. Send content*\n"
        "Paste a URL or type a title. I'll auto-detect the type.\n\n"
        "*2. Review preview*\n"
        "I'll generate a review and show you a preview with:\n"
        "  📌 Title — 📂 Type — 💬 Review — ⭐ Rating — 🏷️ Tags\n\n"
        "*3. Choose an action:*\n"
        "  ✅ *Confirm* — Save to your dashboard\n"
        "  ✏️ *Edit* — Modify any field\n"
        "  🔄 *Regenerate* — Get a fresh AI review\n"
        "  ❌ *Cancel* — Discard everything\n\n"
        "*4. Fast mode*\n"
        "Use /fast to toggle. When ON, reviews are saved instantly\n"
        "without preview (for quick adds).\n\n"
        "💡 _Tip: The AI works best with specific titles or clean URLs._",
        parse_mode="Markdown",
    )


@authorized
async def fast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fast — toggle fast mode."""
    session = get_session(update.effective_user.id)
    session.fast_mode = not session.fast_mode
    status = "ON ⚡" if session.fast_mode else "OFF 🐢"
    await update.message.reply_text(
        f"🔀 Fast mode is now *{status}*\n\n"
        f"{'Reviews will be saved instantly without preview.' if session.fast_mode else 'You will see a preview before saving.'}",
        parse_mode="Markdown",
    )


@authorized
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel — discard current operation."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    if session.state == "idle":
        await update.message.reply_text("ℹ️ Nothing to cancel.")
        return
    clear_session(user_id)
    await update.message.reply_text("❌ Operation cancelled. Session cleared.")


# ─── Main Text Input Handler ─────────────────────────────────────────


@authorized
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any text message — the main entry point for content curation."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    text = update.message.text.strip()

    # If we're in editing_field state, route to edit handler
    if session.state == "editing_field":
        await _handle_edit_value(update, context, session, text)
        return

    # If there's already a pending review, tell user to act on it
    if session.state in ("pending", "editing"):
        await update.message.reply_text(
            "⚠️ You have a pending review. Please ✅ Confirm, ✏️ Edit, 🔄 Regenerate, or ❌ Cancel it first.\n\n"
            "Or use /cancel to discard it.",
            parse_mode="Markdown",
        )
        return

    # Start processing new input
    processing_msg = await update.message.reply_text("🔍 Analyzing your content...")

    try:
        # Extract URL and detect type
        url = extract_url(text)
        content_type = detect_content_type(text, url)

        # Fetch metadata if URL found
        metadata = None
        if url:
            await processing_msg.edit_text("🌐 Fetching metadata...")
            metadata = await fetch_url_metadata(url)

        # Generate AI review
        await processing_msg.edit_text("🤖 Generating review...")
        data = await generate_review(text, content_type, metadata)

        # Attach URL if found
        if url:
            data["url"] = url

        # Store in session
        set_session_data(user_id, data, text)

        # Fast mode: save immediately
        if session.fast_mode:
            await processing_msg.edit_text("⚡ Saving (fast mode)...")
            await save_resonance_entry(data)
            clear_session(user_id)
            await processing_msg.edit_text(
                format_success(data),
                parse_mode="Markdown",
            )
            return

        # Normal mode: show preview with action buttons
        session = get_session(user_id)  # refresh after set_session_data
        preview_text = format_preview(data)
        preview_msg = await processing_msg.edit_text(
            preview_text,
            parse_mode="Markdown",
            reply_markup=preview_keyboard(),
        )
        session.preview_message_id = preview_msg.message_id

    except ValueError as e:
        log.error("Review generation failed: %s", e)
        await processing_msg.edit_text(
            f"❌ *Error:* {e}\n\nPlease try again with a different input.",
            parse_mode="Markdown",
        )
        clear_session(user_id)
    except Exception as e:
        log.error("Unexpected error in handle_input: %s", e, exc_info=True)
        await processing_msg.edit_text(
            "❌ Something went wrong. Please try again.",
            parse_mode="Markdown",
        )
        clear_session(user_id)


# ─── Callback Query Handler ──────────────────────────────────────────


@authorized
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)
    data_str = query.data

    # ── Confirm ──
    if data_str == "confirm":
        if session.state not in ("pending", "editing"):
            await query.edit_message_text("⚠️ No pending review to confirm.")
            return

        try:
            await query.edit_message_text("💾 Saving to your dashboard...")
            await save_resonance_entry(session.data)
            await query.edit_message_text(
                format_success(session.data),
                parse_mode="Markdown",
            )
            clear_session(user_id)
        except Exception as e:
            log.error("Save failed: %s", e)
            await query.edit_message_text(
                f"❌ Save failed: {e}\n\nTry again with ✅ Confirm.",
                reply_markup=preview_keyboard(),
            )

    # ── Edit ──
    elif data_str == "edit":
        if session.state not in ("pending", "editing"):
            await query.edit_message_text("⚠️ No pending review to edit.")
            return
        session.state = "editing"
        await query.edit_message_text(
            "✏️ *Which field would you like to edit?*",
            parse_mode="Markdown",
            reply_markup=edit_field_keyboard(),
        )

    # ── Edit specific field ──
    elif data_str.startswith("edit_"):
        field_name = data_str.replace("edit_", "")

        if field_name == "type":
            await query.edit_message_text(
                "📂 *Select the content type:*",
                parse_mode="Markdown",
                reply_markup=type_selection_keyboard(),
            )
            return

        if field_name == "rating":
            await query.edit_message_text(
                "⭐ *Select the rating:*",
                parse_mode="Markdown",
                reply_markup=rating_keyboard(),
            )
            return

        # Title or Review — ask for text input
        session.state = "editing_field"
        session.editing_field = field_name

        field_labels = {"title": "📌 Title", "review": "💬 Review"}
        label = field_labels.get(field_name, field_name)

        current = session.data.get(field_name, "")
        await query.edit_message_text(
            f"✏️ *Editing {label}*\n\n"
            f"Current: _{current}_\n\n"
            "Type the new value:",
            parse_mode="Markdown",
        )

    # ── Set type via keyboard ──
    elif data_str.startswith("set_type_"):
        new_type = data_str.replace("set_type_", "")
        session.data["type"] = new_type
        session.state = "pending"
        await query.edit_message_text(
            format_preview(session.data),
            parse_mode="Markdown",
            reply_markup=preview_keyboard(),
        )

    # ── Set rating via keyboard ──
    elif data_str.startswith("set_rating_"):
        new_rating = int(data_str.replace("set_rating_", ""))
        session.data["rating"] = new_rating
        session.state = "pending"
        await query.edit_message_text(
            format_preview(session.data),
            parse_mode="Markdown",
            reply_markup=preview_keyboard(),
        )

    # ── Back to preview ──
    elif data_str == "back_to_preview":
        session.state = "pending"
        await query.edit_message_text(
            format_preview(session.data),
            parse_mode="Markdown",
            reply_markup=preview_keyboard(),
        )

    # ── Regenerate ──
    elif data_str == "regenerate":
        if not session.original_input:
            await query.edit_message_text("⚠️ No content to regenerate.")
            return

        await query.edit_message_text("🔄 Regenerating review...")

        try:
            url = extract_url(session.original_input)
            content_type = detect_content_type(session.original_input, url)
            metadata = await fetch_url_metadata(url) if url else None
            data = await generate_review(session.original_input, content_type, metadata)

            if url:
                data["url"] = url

            set_session_data(user_id, data, session.original_input)

            await query.edit_message_text(
                format_preview(data),
                parse_mode="Markdown",
                reply_markup=preview_keyboard(),
            )
        except Exception as e:
            log.error("Regeneration failed: %s", e)
            await query.edit_message_text(
                f"❌ Regeneration failed: {e}\n\nTry again:",
                reply_markup=preview_keyboard(),
            )

    # ── Cancel ──
    elif data_str == "cancel":
        clear_session(user_id)
        await query.edit_message_text("❌ Cancelled. Entry discarded.")


# ─── Edit Value Handler ──────────────────────────────────────────────


async def _handle_edit_value(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session,
    new_value: str,
):
    """Process text input when the user is editing a specific field."""
    field = session.editing_field

    if field == "title":
        session.data["title"] = new_value
    elif field == "review":
        session.data["review"] = new_value
    else:
        await update.message.reply_text("⚠️ Unknown field. Operation cancelled.")
        session.state = "pending"
        session.editing_field = None
        return

    session.state = "pending"
    session.editing_field = None

    await update.message.reply_text(
        format_preview(session.data),
        parse_mode="Markdown",
        reply_markup=preview_keyboard(),
    )
