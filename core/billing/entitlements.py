from core.models.user import User


def can_generate_site(user: User) -> bool:
    """User needs at least 1 credit to generate a site."""
    return user.has_credits


def next_credit_type(user: User) -> str:
    """
    Returns which credit bucket will be consumed on the next generation.
    'paid'  → page is permanent (no trial).
    'free'  → page gets a 7-day trial, then is paused.
    """
    if user.paid_credits > 0:
        return "paid"
    return "free"
