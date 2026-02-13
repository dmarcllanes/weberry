from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.services.project_service import update_text_content
from user_app.frontend.pages.edit import edit_page


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


async def show_edit_page(req, project_id: str):
    """Show the edit-content page with editable text fields."""
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    if not project.site_version or not project.site_version.html:
        return error_page("No site content to edit")

    return edit_page(project)


async def edit_content(req, project_id: str):
    """
    Handle multi-field text edits from the edit page.
    Reads original_{i} / edited_{i} pairs, builds updates dict,
    calls update_text_content for changed fields only.
    """
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    form = await req.form()

    updates = {}
    i = 0
    while True:
        original_key = f"original_{i}"
        edited_key = f"edited_{i}"
        if original_key not in form:
            break
        original = form.get(original_key, "")
        edited = form.get(edited_key, "")
        if original != edited and original:
            updates[original] = edited
        i += 1

    if updates:
        try:
            update_text_content(project, updates)
        except CoreError as e:
            return error_page(str(e))

    return RedirectResponse(f"/projects/{project_id}/edit", status_code=303)
