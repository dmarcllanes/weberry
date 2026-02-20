from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.services.project_service import update_text_content, rerender_site
from user_app.frontend.pages.edit import edit_page
import uuid
import io
from PIL import Image
from config.settings import SUPABASE_ASSETS_BUCKET


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

    return RedirectResponse(f"/pages/{project_id}", status_code=303)


async def show_edit_page(req, project_id: str):
    """Show the edit-content page with editable text fields."""
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    if not project.site_version or not project.site_version.html:
        return error_page("No site content to edit")

    return edit_page(user, project)


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

    return RedirectResponse(f"/pages/{project_id}/edit", status_code=303)


async def bulk_upload_images(req, project_id: str):
    """Upload multiple images and assign them to template image slots in order."""
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    plan = project.site_plan
    if not plan:
        return error_page("No site plan found")

    from core.ai.template_loader import load_template_manifest
    try:
        manifest = load_template_manifest(plan.selected_template)
    except FileNotFoundError:
        return error_page("Template not found")

    slots = list(manifest.get("slots", {}).keys())
    if not slots:
        return error_page("No image slots in this template")

    form = await req.form()
    files = form.getlist("files")
    if not files:
        return error_page("No files uploaded")

    storage = db.get_storage()
    uploaded_count = 0

    for slot_name, upload in zip(slots, files):
        if not hasattr(upload, "read"):
            continue
        contents = await upload.read()
        if not contents or len(contents) > 5 * 1024 * 1024:
            continue
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except Exception:
            continue

        ext = upload.filename.rsplit(".", 1)[-1] if "." in upload.filename else "png"
        storage_path = f"{project_id}/assets/{uuid.uuid4().hex}.{ext}"
        content_type = upload.content_type or "image/png"
        storage.from_(SUPABASE_ASSETS_BUCKET).upload(storage_path, contents, {"content-type": content_type})
        public_url = storage.from_(SUPABASE_ASSETS_BUCKET).get_public_url(storage_path)
        plan.image_overrides[slot_name] = public_url
        uploaded_count += 1

    if uploaded_count == 0:
        return error_page("No valid images were uploaded")

    try:
        rerender_site(project)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{project_id}", status_code=303)


async def edit_image(req, project_id: str):
    """
    Handle image slot updates (keyword change or file upload).
    Expects form fields: 
      - slot_name: str
      - action: "keyword" | "upload"
      - keyword: str (if action=keyword)
      - file: UploadFile (if action=upload)
    """
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)
        
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
            # simple validation
            img.verify() 
        except Exception:
            return error_page("Invalid image file")
            
        # Upload to supabase
        ext = upload.filename.rsplit(".", 1)[-1] if "." in upload.filename else "png"
        storage_path = f"{project_id}/assets/{uuid.uuid4().hex}.{ext}"
        content_type = upload.content_type or "image/png"
        
        storage = db.get_storage()
        # Reset file pointer for upload
        img_buffer = io.BytesIO(contents)
        storage.from_(SUPABASE_ASSETS_BUCKET).upload(storage_path, img_buffer.getvalue(), {"content-type": content_type})
        public_url = storage.from_(SUPABASE_ASSETS_BUCKET).get_public_url(storage_path)
        
        # Set override
        plan.image_overrides[slot_name] = public_url
        
    else:
        return error_page("Invalid action")
        
    # Persist plan changes (db.save_project called inside rerender_site but we need to save plan modifications first?
    # Actually db.save_project saves the whole project including plan. 
    # But rerender_site reads from project object in memory.
    # So we just need to update the object in memory and then call rerender_site which saves it.
    
    # Wait, rerender_site saves the project. So we are good.
    try:
        rerender_site(project)
    except CoreError as e:
        return error_page(str(e))
        
    # Return to preview (or whereever)
    # If called from an iframe or htmx, we might want to return just the updated image?
    # But for simplicity, redirect to preview which reloads.
    return RedirectResponse(f"/pages/{project_id}", status_code=303)
