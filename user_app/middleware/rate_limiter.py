"""In-memory sliding window rate limiter.

No Redis — single-process, state resets on server restart.
Used to protect expensive and public-facing endpoints from flooding.
"""

import time
from collections import defaultdict

from fasthtml.common import Response

# {key: [monotonic_timestamp, ...]}
_store: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """Sliding window check. Returns True if the key has exceeded the limit.

    Side-effect: records this request if under the limit.
    """
    now = time.monotonic()
    cutoff = now - window_seconds
    history = _store[key]

    # Prune entries outside the window
    while history and history[0] < cutoff:
        history.pop(0)

    if len(history) >= limit:
        return True

    history.append(now)
    return False


def rate_limit_response(message: str = "Too many requests. Please slow down.") -> Response:
    return Response(message, status_code=429)
