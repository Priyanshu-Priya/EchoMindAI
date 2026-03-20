"""
State machine / Context manager.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UserSession:
    state: str = "idle"
    # "resonance" or "thought" or "routing"
    domain: str = ""
    # Data being built:
    data: dict = field(default_factory=dict)
    
    # Original text
    original_input: str = ""
    temp_text: str = ""
    
    # Which field is being interactively edited?
    editing_field: Optional[str] = None
    
    # Track the message ID of the active preview so we can edit it
    preview_message_id: Optional[int] = None
    
    # User pref
    fast_mode: bool = False


# In-memory store: user_id -> UserSession
_sessions = {}


def get_session(user_id: int) -> UserSession:
    """Retrieve or create a session for a user."""
    if user_id not in _sessions:
        _sessions[user_id] = UserSession()
    return _sessions[user_id]


def clear_session(user_id: int):
    """Reset the user's session state and data, preserving fast_mode pref."""
    if user_id in _sessions:
        fast_mode = _sessions[user_id].fast_mode
        _sessions[user_id] = UserSession(fast_mode=fast_mode)


def set_session_data(user_id: int, data: dict, original_input: str, domain: str = "resonance"):
    """Update a session with fully generated data payload."""
    sess = get_session(user_id)
    sess.data = data
    sess.original_input = original_input
    sess.domain = domain
    sess.state = "pending"
