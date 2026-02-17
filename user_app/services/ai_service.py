from core.ai.gateway import generate_plan, generate_site, generate_and_render
from core.ai.schemas import SitePlan
from core.models.project import Project
from core.models.user import User
from core.models.site_version import SiteVersion
from core.state_machine.states import ProjectState
from core.errors import CoreError
from user_app import db


def run_planner_for_project(project: Project, user: User) -> SitePlan:
    """
    Service-layer entry point for planning.
    Validates state, calls the gateway, then persists the result.
    """
    if project.state != ProjectState.MEMORY_READY:
        raise CoreError("Project must be in memory_ready state to run planner")
    plan = generate_plan(project, user)
    db.save_project(project)
    return plan


def run_generator_for_project(project: Project, user: User) -> SiteVersion:
    """
    Service-layer entry point for site generation.
    Validates state, calls the gateway, then persists the result.
    """
    if project.state != ProjectState.PLAN_APPROVED:
        raise CoreError("Project must be in plan_approved state to generate site")
    site_version = generate_site(project, user)
    db.save_project(project)
    return site_version


def run_generate_and_render(project: Project, user: User) -> SiteVersion:
    """
    Template flow: AI picks template + writes copy, Jinja2 renders.
    MEMORY_READY -> SITE_GENERATED in one shot.
    """
    if project.state != ProjectState.MEMORY_READY:
        raise CoreError("Project must be in memory_ready state to generate")
    site_version = generate_and_render(project, user)
    db.save_project(project)
    return site_version
