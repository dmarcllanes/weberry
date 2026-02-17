"""
Session-based auth: reads user_id from server session, fetches from DB.
"""

from core.models.user import User
from user_app import db


def get_current_user(session) -> User | None:
    """Return the logged-in User from the session, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.get_user(user_id)


def get_or_create_user(user_id: str, email: str, full_name: str | None = None, avatar_url: str | None = None) -> User:
    """Upsert user on login and return the User object."""
    return db.upsert_user(user_id, email, full_name, avatar_url)
