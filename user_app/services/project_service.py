from core.models.user import User
from core.models.project import Project
from core.models.brand_memory import BrandMemory
from core.state_machine.engine import transition
from core.state_machine.states import ProjectState
from core.billing.entitlements import can_create_project
from core.errors import CoreError
from user_app import db


class ProjectLimitError(CoreError):
    def __init__(self):
        super().__init__("Project limit reached for your plan")


def create_project_for_user(user: User) -> Project:
    count = db.count_projects_for_user(user.id)
    if not can_create_project(user, count):
        raise ProjectLimitError()
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
