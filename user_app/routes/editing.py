from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.middleware.rate_limiter import is_rate_limited, rate_limit_response
from user_app.services.project_service import update_text_content, rerender_site
from user_app.frontend.pages.edit import edit_page
import uuid
import io
from PIL import Image
from config.settings import SUPABASE_ASSETS_BUCKET


async def edit_text(req, page_id: str):
    """
    Apply text-only edits to the site HTML.
    Expects form fields: old_text, new_text
    Does NOT trigger AI.
    """
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    form = await req.form()
    old_text = form.get("old_text", "")
    new_text = form.get("new_text", "")

    if not old_text:
        return error_page("Original text is required")

    try:
        update_text_content(project, {old_text: new_text})
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{page_id}", status_code=303)


async def show_edit_page(req, page_id: str):
    """Show the edit-content page with editable text fields or HTML editor."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    if not project.site_version or not project.site_version.html:
        return error_page("No site content to edit")

    active_tab = req.query_params.get("tab", "visual")
    if active_tab not in ("visual", "text", "html"):
        active_tab = "visual"
    return edit_page(user, project, active_tab=active_tab)


async def edit_content(req, page_id: str):
    """
    Handle multi-field text edits from the edit page.
    Reads original_{i} / edited_{i} pairs, builds updates dict,
    calls update_text_content for changed fields only.
    """
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

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

    return RedirectResponse(f"/pages/{page_id}/edit?tab=text", status_code=303)


async def edit_html(req, page_id: str):
    """Save raw HTML edits directly to site_version.html."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    if not project.site_version:
        return error_page("No site content to edit")

    form = await req.form()
    new_html = form.get("html", "")
    if not new_html.strip():
        return error_page("HTML content cannot be empty")

    project.site_version.html = new_html
    db.save_project(project)

    return RedirectResponse(f"/pages/{page_id}/edit?tab=html", status_code=303)




async def edit_image(req, page_id: str):
    """
    Handle image slot updates (keyword change or file upload).
    Expects form fields:
      - slot_name: str
      - action: "keyword" | "upload"
      - keyword: str (if action=keyword)
      - file: UploadFile (if action=upload)
    """
    user = req.scope["user"]
    if is_rate_limited(f"edit_image:{user.id}", limit=30, window_seconds=3600):
        return rate_limit_response("Too many image edits. Please wait before trying again.")
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    form = await req.form()
    slot_name = form.get("slot_name")
    action = form.get("action")

    if not slot_name or not action:
        return error_page("Missing slot_name or action")

    plan = project.site_plan
    if not plan:
        return error_page("No site plan found")

    if action == "keyword":
        keyword = form.get("keyword", "").strip()
        if not keyword:
            return error_page("Keyword required")

        # Update keyword
        plan.image_keywords[slot_name] = keyword
        # Remove override if exists so keyword takes precedence
        if slot_name in plan.image_overrides:
            del plan.image_overrides[slot_name]

    elif action == "upload":
        upload = form.get("file")
        if not hasattr(upload, "read"):
            return error_page("Invalid file upload")

        contents = await upload.read()
        if len(contents) > 5 * 1024 * 1024:
            return error_page("File too large (max 5MB)")

        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except Exception:
            return error_page("Invalid image file")

        ext = upload.filename.rsplit(".", 1)[-1] if "." in upload.filename else "png"
        storage_path = f"{page_id}/assets/{uuid.uuid4().hex}.{ext}"
        content_type = upload.content_type or "image/png"

        storage = db.get_storage()
        img_buffer = io.BytesIO(contents)
        storage.from_(SUPABASE_ASSETS_BUCKET).upload(storage_path, img_buffer.getvalue(), {"content-type": content_type})
        public_url = storage.from_(SUPABASE_ASSETS_BUCKET).get_public_url(storage_path)

        # Set override
        plan.image_overrides[slot_name] = public_url

    else:
        return error_page("Invalid action")

    try:
        rerender_site(project)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{page_id}", status_code=303)
