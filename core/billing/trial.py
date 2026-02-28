from datetime import datetime, timezone


def is_trial_active(trial_ends_at: datetime | None) -> bool:
    if trial_ends_at is None:
        return False
    return datetime.now(timezone.utc) < trial_ends_at


def is_trial_expired(trial_ends_at: datetime | None) -> bool:
    if trial_ends_at is None:
        return False
    return datetime.now(timezone.utc) >= trial_ends_at


def days_remaining(trial_ends_at: datetime | None) -> int:
    if trial_ends_at is None:
        return 0
    delta = trial_ends_at - datetime.now(timezone.utc)
    if delta.total_seconds() <= 0:
        return 0
    return delta.days + (1 if delta.seconds > 0 else 0)
