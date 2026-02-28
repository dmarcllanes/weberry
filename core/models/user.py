from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class User:
    id: str
    email: str
    paid_credits: int = 0
    free_credits: int = 1
    free_credits_expires_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    avatar_url: str | None = None
    full_name: str | None = None
    lemon_squeezy_customer_id: str | None = None

    @property
    def available_credits(self) -> int:
        return self.paid_credits + (self.free_credits if self.free_credit_active else 0)

    @property
    def has_credits(self) -> bool:
        return self.available_credits > 0

    @property
    def free_credit_active(self) -> bool:
        if self.free_credits_expires_at is None or self.free_credits <= 0:
            return False
        expires: datetime = self.free_credits_expires_at  # type: ignore[assignment]
        return datetime.now(timezone.utc) < expires
