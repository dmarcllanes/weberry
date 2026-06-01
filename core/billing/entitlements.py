from core.models.user import User

# TESTING MODE — credit limits disabled
_LIMITS_DISABLED = True


def can_generate_site(user: User) -> bool:
    if _LIMITS_DISABLED:
        return True
    return user.has_credits


def next_credit_type(user: User) -> str:
    if _LIMITS_DISABLED:
        return "paid"
    if user.paid_credits > 0:
        return "paid"
    return "free"
