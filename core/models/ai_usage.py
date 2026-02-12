from dataclasses import dataclass
from datetime import datetime


@dataclass
class AIUsage:
    planner_calls: int = 0
    generation_calls: int = 0
    last_ai_call_at: datetime | None = None
