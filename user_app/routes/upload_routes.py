"""Routes for raw-template image upload and asset serving."""

import io
import logging
import uuid
from pathlib import Path

log = logging.getLogger(__name__)

from fasthtml.common import RedirectResponse, Response
from PIL import Image
from starlette.responses import FileResponse

from config.settings import SUPABASE_ASSETS_BUCKET
from core.models.brand_memory import BrandMemory, LabeledAsset
from core.raw_template.loader import get_raw_template
from core.raw_template.slot_analyzer import analyze_slots
from core.state_machine.engine import transition
from core.state_machine.states import ProjectState
from user_app import db
from user_app.routes import error_page
from user_app.frontend.pages.image_upload import image_upload_page

_TEMPLATE_BASE = Path(__file__).parent.parent.parent / "template"


def _advance_past_upload(project) -> None:
    """Mark the upload step as done by advancing DRAFT → INPUT_READY, then save."""
    if project.state == ProjectState.DRAFT:
        transition(project, ProjectState.INPUT_READY)
    db.save_project(project)


# ── GET /pages/{page_id}/upload ─────────────────────────────────────────────

async def show_upload(req, page_id: str):
    user    = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)
    if not project.template_id or not get_raw_template(project.template_id):
        return RedirectResponse(f"/pages/{page_id}", status_code=303)
    return image_upload_page(user, project)


# ── POST /pages/{page_id}/upload ────────────────────────────────────────────

async def handle_upload(req, page_id: str):
    user    = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    tpl = get_raw_template(project.template_id or "")
    if not tpl:
        return error_page("Template not found")

    form = await req.form()

    # If user clicked Skip, just redirect to braindump
    if form.get("skip"):
        if not project.brand_memory:
            project.brand_memory = BrandMemory(
                business_name="", website_type="", primary_goal=""
            )
        _advance_past_upload(project)
        return RedirectResponse(f"/pages/{page_id}", status_code=303)

    # Build full list of individual image stems from the template
    slots = analyze_slots(tpl["html_path"])
    all_stems = [
        fname.rsplit(".", 1)[0]
        for slot in slots
        for fname in slot["filenames"]
    ]

    assets = list(project.brand_memory.labeled_assets) if (
        project.brand_memory and project.brand_memory.labeled_assets
    ) else []

    try:
        from user_app.db import get_client as _supabase
        sb = _supabase()
    except Exception:
        sb = None

    for stem in all_stems:
        field  = f"img_{stem}"
        upload = (form.getlist(field) or [None])[0] if hasattr(form, "getlist") else form.get(field)
        fname  = getattr(upload, "filename", None) if upload else None
        if not fname:
            log.debug("[upload] %s — no file submitted for slot '%s', keeping default", page_id, stem)
            continue
        raw = await upload.read()
        if not raw:
            log.warning("[upload] %s — empty file for slot '%s'", page_id, stem)
            continue

        try:
            img           = Image.open(io.BytesIO(raw))
            width, height = img.size
            orient        = _orientation(width, height)
            buf = io.BytesIO()
            img.convert("RGB").save(buf, "JPEG", quality=88)
            buf.seek(0)
            obj_path = f"assets/{user.id}/{page_id}/{uuid.uuid4()}.jpg"
            if sb:
                sb.storage.from_(SUPABASE_ASSETS_BUCKET).upload(
                    obj_path,
                    buf.read(),
                    {"content-type": "image/jpeg", "upsert": "true"},
                )
                url = sb.storage.from_(SUPABASE_ASSETS_BUCKET).get_public_url(obj_path)
            else:
                url = f"/raw-asset/{project.template_id}/assets/{upload.filename}"

            # Store by exact stem so assembler can match e.g. display-3 → display-3.jpg
            assets = [a for a in assets if a.label != stem]
            assets.append(LabeledAsset(
                url=url, label=stem,
                width=width, height=height, orientation=orient,
            ))
            log.info("[upload] %s — saved slot '%s' → %s", page_id, stem, url)
        except Exception as exc:
            log.error("[upload] %s — failed to process slot '%s': %s", page_id, stem, exc)
            continue

    log.info("[upload] %s — final labeled_assets: %s", page_id,
             [(a.label, a.url) for a in assets])

    # Save uploads to project brand_memory
    if not project.brand_memory:
        project.brand_memory = BrandMemory(
            business_name="", website_type="", primary_goal=""
        )
    project.brand_memory.labeled_assets = assets
    _advance_past_upload(project)

    return RedirectResponse(f"/pages/{page_id}", status_code=303)


# ── GET /raw-asset/{rest:path} ───────────────────────────────────────────────

async def serve_raw_asset(req, rest: str):
    """Serve static files from the template/ folder (original template assets)."""
    # Prevent path traversal
    try:
        target = (_TEMPLATE_BASE / rest).resolve()
        _TEMPLATE_BASE.resolve()  # ensure base is resolved
        if not str(target).startswith(str(_TEMPLATE_BASE.resolve())):
            return Response("Forbidden", status_code=403)
    except Exception:
        return Response("Bad request", status_code=400)

    if not target.exists() or not target.is_file():
        return Response("Not found", status_code=404)

    suffix = target.suffix.lower()
    media_types = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml",
        ".css": "text/css", ".js": "application/javascript",
        ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
    }
    media = media_types.get(suffix, "application/octet-stream")
    return FileResponse(str(target), media_type=media, headers={
        "Cache-Control": "public, max-age=86400",
    })


def _orientation(w: int, h: int) -> str:
    if w > h * 1.2:
        return "landscape"
    if h > w * 1.2:
        return "portrait"
    return "square"
