from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.services.project_service import update_text_content


async def edit_text(req, project_id: str):
    """
    Apply text-only edits to the site HTML.
    Expects form fields: old_text, new_text
    Does NOT trigger AI.
    """
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    form = await req.form()
    old_text = form.get("old_text", "")
    new_text = form.get("new_text", "")

    if not old_text:
        return error_page("Original text is required")

    try:
        update_text_content(project, {old_text: new_text})
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/projects/{project_id}", status_code=303)
