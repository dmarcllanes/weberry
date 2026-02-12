from datetime import datetime, timezone
from core.models.ai_usage import AIUsage
from core.errors import AICooldownActive
from config.settings import AI_COOLDOWN_SECONDS


def check_cooldown(usage: AIUsage) -> None:
    """Raise AICooldownActive if not enough time has passed since last AI call."""
    if usage.last_ai_call_at is None:
        return

    now = datetime.now(timezone.utc)
    elapsed = (now - usage.last_ai_call_at).total_seconds()
    remaining = AI_COOLDOWN_SECONDS - elapsed

    if remaining > 0:
        raise AICooldownActive(remaining)
