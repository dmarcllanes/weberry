from dataclasses import dataclass, field
from core.errors import AIValidationError


@dataclass
class SectionPlan:
    id: str
    title: str
    purpose: str
    content_notes: str


@dataclass
class CopyBlock:
    placeholder_key: str  # e.g. "hero_headline"
    content: str          # AI-written text


@dataclass
class SitePlan:
    sections: list[SectionPlan]
    page_title: str
    meta_description: str
    # Template flow fields
    copy_blocks: list[CopyBlock] = field(default_factory=list)
    active_sections: list[str] = field(default_factory=list)
    selected_template: str = ""
    image_keywords: dict[str, str] = field(default_factory=dict)
    image_overrides: dict[str, str] = field(default_factory=dict)


@dataclass
class HTMLOutput:
    html: str


@dataclass
class CSSOutput:
    css: str


def validate_site_plan(plan: SitePlan) -> None:
    """Validate a SitePlan against business rules."""
    issues: list[str] = []

    if not plan.sections:
        issues.append("Site plan must have at least one section")

    if not plan.page_title:
        issues.append("Site plan must have a page title")

    # Must have a section that serves as navigation target
    section_ids = [s.id for s in plan.sections]
    if len(section_ids) != len(set(section_ids)):
        issues.append("Section IDs must be unique")

    if issues:
        raise AIValidationError(issues)
