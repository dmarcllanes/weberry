from dataclasses import dataclass
from enum import Enum


class PlanType(Enum):
    FREE = "FREE"
    PAID = "PAID"


@dataclass
class User:
    id: str
    email: str
    plan: PlanType = PlanType.FREE
