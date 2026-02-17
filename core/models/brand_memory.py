from dataclasses import dataclass, field

from enum import Enum


class ProjectIntent(Enum):
    VALIDATION = "validation"  # Conversion Focus
    PRESENCE = "presence"      # Identity Focus


@dataclass
class LabeledAsset:
    url: str
    label: str  # e.g. "spoon", "profile", "hero"
    width: int
    height: int
    orientation: str  # "portrait", "landscape", "square"
@dataclass
class BrandMemory:
    business_name: str
    website_type: str
    primary_goal: str
    description: str = ""
    theme: str = "professional"
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    tagline: str = ""
    services: list[str] = field(default_factory=list)
    project_intent: ProjectIntent = ProjectIntent.VALIDATION
    labeled_assets: list[LabeledAsset] = field(default_factory=list)
