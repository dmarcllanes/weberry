from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.state_machine.states import ProjectState
from core.models.brand_memory import BrandMemory
from core.models.ai_usage import AIUsage
from core.models.site_version import SiteVersion
from core.ai.schemas import SitePlan


@dataclass
class Project:
    id: str
    user_id: str
    state: ProjectState = ProjectState.DRAFT
    brand_memory: BrandMemory | None = None
    ai_usage: AIUsage = field(default_factory=AIUsage)
    site_plan: SitePlan | None = None
    site_version: SiteVersion | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None
