"""
Session management — per-user state tracking for the review workflow.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserSession:
    """Tracks a single user's active review workflow."""

    state: str = "idle"
    # States: idle → pending → editing → editing_field → idle

    data: dict = field(default_factory=dict)
    # { title, type, review, rating, tags, url }

    original_input: str = ""
    editing_field: Optional[str] = None
    preview_message_id: Optional[int] = None
    fast_mode: bool = False


# In-memory session store  (keyed by Telegram user ID)
_sessions: dict[int, UserSession] = {}


def get_session(user_id: int) -> UserSession:
    """Get or create a session for the given user."""
    if user_id not in _sessions:
        _sessions[user_id] = UserSession()
    return _sessions[user_id]


def clear_session(user_id: int) -> None:
    """Reset a user's session to idle."""
    if user_id in _sessions:
        fast = _sessions[user_id].fast_mode
        _sessions[user_id] = UserSession(fast_mode=fast)


def set_session_data(user_id: int, data: dict, original_input: str) -> UserSession:
    """Store AI-generated data and move session to 'pending'."""
    session = get_session(user_id)
    session.data = data
    session.original_input = original_input
    session.state = "pending"
    session.editing_field = None
    return session
