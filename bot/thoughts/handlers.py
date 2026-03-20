"""
Thoughts Handlers — Workflow for capturing observations.
"""

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.auth import authorized
from bot.core.session import get_session, clear_session
from bot.thoughts.keyboards import mood_keyboard, visibility_keyboard, thought_preview_keyboard
from bot.thoughts.formatter import thought_preview, thought_success
from bot.thoughts.db_repo import save_thought_entry
from bot.core.logger import log


@authorized
async def handle_thought_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router for all thought-specific inline button callbacks."""
    query = update.callback_query
    data_str = query.data
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    # ── Initial routing from core router ──
    if data_str == "route_thought":
        session.domain = "thought"
        session.state = "selecting_mood"
        
        # Initialize the thought data dictionary
        session.data = {
            "content": session.temp_text,
            "mood": "",
            "is_published": False
        }
        
        await query.edit_message_text(
            f"*{session.temp_text}*\n\nWhat's your mood for this thought?",
            parse_mode="Markdown",
            reply_markup=mood_keyboard()
        )
        return True

    # ── Custom Mood ──
    if data_str == "mood_custom":
        session.state = "editing_custom_mood"
        await query.edit_message_text(
            "✍️ Type your custom mood and send it to me:",
            parse_mode="Markdown"
        )
        return True

    # ── Preset Mood ──
    if data_str.startswith("mood_"):
        selected_mood = data_str.replace("mood_", "")
        
        if selected_mood == "none":
            session.data["mood"] = ""
            msg = "Mood skipped.\n\nDo you want to publish this immediately?"
        else:
            session.data["mood"] = selected_mood
            msg = f"Mood set to: {selected_mood}\n\nDo you want to publish this immediately?"
            
        session.state = "selecting_visibility"
        await query.edit_message_text(
            msg,
            reply_markup=visibility_keyboard()
        )
        return True
        
    # ── Visibility ──
    if data_str.startswith("vis_"):
        is_pub = "public" in data_str
        session.data["is_published"] = is_pub
        session.state = "pending"
        
        await query.edit_message_text(
            thought_preview(session.data),
            parse_mode="Markdown",
            reply_markup=thought_preview_keyboard()
        )
        return True

    # ── Confirm / Save ──
    if data_str == "thought_confirm":
        if session.state != "pending":
            await query.edit_message_text("⚠️ No pending thought to confirm.")
            return True

        try:
            await query.edit_message_text("💾 Saving thought...")
            save_thought_entry(session.data)
            await query.edit_message_text(
                thought_success(session.data),
                parse_mode="Markdown",
            )
            clear_session(user_id)
        except Exception as e:
            log.error("Failed to save thought: %s", e)
            await query.edit_message_text(
                f"❌ Save failed: {e}\n\nTry again with ✅ Post Thought.",
                reply_markup=thought_preview_keyboard(),
            )
        return True


@authorized
async def process_thought_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input when the user is explicitly in a Thought state (e.g. typing a custom mood)."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    text = update.message.text.strip()
    
    if session.state == "editing_custom_mood":
        session.data["mood"] = text
        session.state = "selecting_visibility"
        
        await update.message.reply_text(
            f"Mood set to: {text}\n\nDo you want to publish this immediately?",
            reply_markup=visibility_keyboard()
        )
        return
        
    await update.message.reply_text("⚠️ Unknown state in Thought workflow. /cancel to start over.")
