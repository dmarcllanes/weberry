from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field


class PlanType(Enum):
    DRAFTER = "DRAFTER"
    VALIDATOR = "VALIDATOR"
    AGENCY = "AGENCY"


@dataclass
class User:
    id: str
    email: str
    plan: PlanType = PlanType.DRAFTER
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    avatar_url: str | None = None
    full_name: str | None = None
