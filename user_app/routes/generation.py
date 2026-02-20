from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.services.ai_service import (
    run_planner_for_project,
    run_generator_for_project,
    run_generate_and_render,
)
from user_app.services.project_service import approve_plan, move_to_preview


async def run_planner(req, project_id: str):
    """Template flow: generate + render in one shot, then go to preview."""
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    try:
        run_generate_and_render(project, user)
    except CoreError as e:
        return error_page(str(e))

    # Auto-transition to PREVIEW
    project = db.get_project(project_id)
    try:
        move_to_preview(project)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{project_id}", status_code=303)


async def approve(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    try:
        approve_plan(project)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{project_id}", status_code=303)


async def run_generator(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    try:
        run_generator_for_project(project, user)
    except CoreError as e:
        return error_page(str(e))

    # Move to preview after generation
    project = db.get_project(project_id)
    try:
        move_to_preview(project)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{project_id}", status_code=303)
