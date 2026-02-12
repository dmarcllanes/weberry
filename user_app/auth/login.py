"""
Auth stub: always returns the dev user.
Replace with real auth (OAuth, sessions, etc.) later.
"""

from core.models.user import User
from user_app import db

STUB_USER_ID = "00000000-0000-0000-0000-000000000001"


def get_current_user() -> User:
    user = db.get_user(STUB_USER_ID)
    if user is None:
        raise RuntimeError(
            f"Stub user {STUB_USER_ID} not found. Run: python -m scripts.seed"
        )
    return user
