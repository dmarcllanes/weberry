import time
from core.errors import AIRateLimited
from config.settings import RATE_LIMIT_MAX_CALLS, RATE_LIMIT_WINDOW_SECONDS

# In-memory sliding window: maps user_id -> list of timestamps
_call_log: dict[str, list[float]] = {}


def check_rate_limit(user_id: str) -> None:
    """Raise AIRateLimited if the user has exceeded the rate limit window."""
    now = time.monotonic()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    timestamps = _call_log.get(user_id, [])

    # Prune old entries
    timestamps = [t for t in timestamps if t > cutoff]
    _call_log[user_id] = timestamps

    if len(timestamps) >= RATE_LIMIT_MAX_CALLS:
        raise AIRateLimited()


def record_call(user_id: str) -> None:
    """Record a new AI call timestamp for rate limiting."""
    now = time.monotonic()
    if user_id not in _call_log:
        _call_log[user_id] = []
    _call_log[user_id].append(now)


def reset(user_id: str | None = None) -> None:
    """Reset rate limit state. For testing only."""
    if user_id:
        _call_log.pop(user_id, None)
    else:
        _call_log.clear()
