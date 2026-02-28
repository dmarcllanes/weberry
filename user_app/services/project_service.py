from core.models.user import User
from core.models.project import Project
from core.models.brand_memory import BrandMemory
from core.state_machine.engine import transition
from core.state_machine.states import ProjectState
from core.errors import CoreError
from user_app import db


def create_project_for_user(user: User) -> Project:
    # Creating a draft is free — credits are checked at generation time (braindump).
    project = db.create_project(user.id)
    return project


def get_user_project(user: User) -> Project | None:
    projects = db.get_projects_for_user(user.id)
    if not projects:
        return None
    return projects[0]


def get_user_projects(user: User) -> list[Project]:
    return db.get_projects_for_user(user.id)


def save_brand_memory(project: Project, memory: BrandMemory) -> None:
    project.brand_memory = memory
    if project.state == ProjectState.DRAFT:
        transition(project, ProjectState.INPUT_READY)
    if project.state == ProjectState.INPUT_READY:
        transition(project, ProjectState.MEMORY_READY)
    db.save_project(project)


def approve_plan(project: Project) -> None:
    transition(project, ProjectState.PLAN_APPROVED)
    db.save_project(project)


def move_to_preview(project: Project) -> None:
    transition(project, ProjectState.PREVIEW)
    db.save_project(project)


def update_text_content(project: Project, updates: dict[str, str]) -> None:
    """
    Apply text-only edits to the site HTML.
    Does NOT trigger AI. Users may fix typos and change wording.
    """
    if project.site_version is None:
        raise CoreError("No site version to edit")

    html = project.site_version.html
    for old_text, new_text in updates.items():
        html = html.replace(old_text, new_text)

    project.site_version.html = html
    db.save_project(project)


def rerender_site(project: Project) -> None:
    """Re-render the template with current plan/memory (e.g. after image update)."""
    # Local import to avoid circular dependency
    from core.ai.template_renderer import render_template

    if not project.site_plan or not project.site_plan.selected_template:
        raise CoreError("No site plan or template selected")

    site_version = render_template(
        project.site_plan.selected_template,
        project.site_plan,
        project.brand_memory
    )
    project.site_version = site_version
    db.save_project(project)
