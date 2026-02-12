from dataclasses import dataclass
from core.errors import AIValidationError


@dataclass
class SectionPlan:
    id: str
    title: str
    purpose: str
    content_notes: str


@dataclass
class SitePlan:
    sections: list[SectionPlan]
    page_title: str
    meta_description: str


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
