import io
import uuid

from PIL import Image
from fasthtml.common import RedirectResponse, Response, Div, P

from core.models.brand_memory import BrandMemory, ProjectIntent, LabeledAsset
from core.state_machine.states import ProjectState
from core.billing.trial import days_remaining as trial_days_remaining
from config.settings import SUPABASE_ASSETS_BUCKET
from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from core.billing.entitlements import can_create_project
from user_app.middleware.rate_limiter import is_rate_limited, rate_limit_response
from user_app.services.project_service import (
    create_project_for_user,
    get_user_projects,
    save_brand_memory,
    move_to_preview,
)
from user_app.services.ai_service import run_generate_and_render
from user_app.frontend.pages.dashboard import dashboard_page
from user_app.frontend.pages.onboarding import onboarding_page, waiting_for_plan_page
from user_app.frontend.pages.plan_review import plan_review_page
from user_app.frontend.pages.generating import generating_page
from user_app.frontend.pages.preview import preview_page
from user_app.frontend.pages.publish import published_page
from user_app.frontend.pages.profile import user_profile_page, brand_profile_page, brand_info_component
from user_app.frontend.pages.site_detail import site_detail_page


async def get_brand_details(req, page_id: str):
    """Return only the brand info component for HTMX modal loading."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return Div(P("Page not found.", style="text-align:center;padding:2rem;color:#991B1B"))
    try:
        return brand_info_component(project)
    except Exception as e:
        return Div(P(f"Could not load details: {e}", style="text-align:center;padding:2rem;color:#991B1B"))


def dashboard(req):
    user = req.scope["user"]
    projects = get_user_projects(user)

    # Extract query params
    tab = req.query_params.get("tab", "unfinished")
    try:
        page = int(req.query_params.get("page", "1"))
    except ValueError:
        page = 1

    # Always show dashboard to allow creating new pages/managing existing ones
    show_new = can_create_project(user, len(projects))
    return dashboard_page(user, projects, show_new_button=show_new, active_tab=tab, page=page)


def show_user_profile(req):
    """Top-level /profile — show user account info only."""
    user = req.scope["user"]
    return user_profile_page(user)


def create_page(req):
    user = req.scope["user"]
    try:
        project = create_project_for_user(user)
    except CoreError as e:
        return error_page(str(e))
    return RedirectResponse(f"/pages/{project.id}", status_code=303)


async def show_page(req, page_id: str):
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    state = project.state

    # Route to the correct page based on project state
    if state in (ProjectState.DRAFT, ProjectState.INPUT_READY):
        return onboarding_page(user, project)

    if state == ProjectState.MEMORY_READY:
        return waiting_for_plan_page(user, project)

    if state == ProjectState.PLAN_READY:
        # Legacy flow — show plan review
        return plan_review_page(user, project)

    if state == ProjectState.PLAN_APPROVED:
        # Legacy flow — show generating page
        return generating_page(user, project)

    if state in (ProjectState.SITE_GENERATED, ProjectState.PREVIEW):
        return preview_page(user, project)

    if state == ProjectState.PUBLISHED:
        base = str(req.url.scheme) + "://" + req.headers.get("host", "localhost")
        public_url = f"{base}/sites/{page_id}"
        row = db.get_project_row(page_id)
        trial_info = None
        if row and row.get("trial_ends_at"):
            from datetime import datetime
            trial_ends = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]
            trial_info = {"days_remaining": trial_days_remaining(trial_ends)}
        return published_page(user, project, public_url, trial_info)

    return error_page("Unknown page state")


async def preview_render(req, page_id: str):
    """Serve the generated HTML for the preview iframe."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return Response("Not found", status_code=404)

    if not project.site_version or not project.site_version.html:
        return Response("<p>No preview available yet.</p>", media_type="text/html")

    html = project.site_version.html
    css = project.site_version.css or ""
    # Strip any legacy <script> tags from stored HTML
    import re
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    if css:
        html = html.replace("</head>", f"<style>{css}</style></head>", 1)
    # Inject mobile nav toggle JS (kept out of stored HTML for validation)
    from core.publishing.renderer import inject_nav_js
    html = inject_nav_js(html)
    return Response(html, media_type="text/html")


async def show_profile(req, page_id: str):
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)
    return brand_profile_page(project)


async def show_site(req, page_id: str):
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    public_url = None
    trial_info = None
    if project.state == ProjectState.PUBLISHED:
        base = str(req.url.scheme) + "://" + req.headers.get("host", "localhost")
        public_url = f"{base}/sites/{page_id}"
        row = db.get_project_row(page_id)
        if row and row.get("trial_ends_at"):
            from datetime import datetime
            trial_ends = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]
            trial_info = {"days_remaining": trial_days_remaining(trial_ends)}

    return site_detail_page(user, project, public_url, trial_info)


async def delete_page(req, page_id: str):
    """Delete a page and redirect to dashboard."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    db.delete_project(page_id)
    return RedirectResponse("/pages", status_code=303)


def _auto_label(width, height, index):
    """Auto-assign a label based on image dimensions and position."""
    ratio = width / height if height else 1
    if ratio >= 1.8:
        return "hero"
    if ratio <= 0.65:
        return "portrait"
    if width >= 1200 and ratio >= 1.2:
        return "hero"
    if index == 0:
        return "hero"
    return "product"


async def upload_asset(req, page_id: str):
    """Upload up to 4 images, auto-read metadata, store in Supabase."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return Response("Not found", status_code=404)

    form = await req.form()
    files = form.getlist("files")

    if not files:
        return Response("No files provided", status_code=400)

    # Enforce 4 image limit
    existing = []
    if project.brand_memory and project.brand_memory.labeled_assets:
        existing = project.brand_memory.labeled_assets
    slots = 4 - len(existing)
    if slots <= 0:
        return Response("Maximum 4 images allowed", status_code=400)
    files = files[:slots]

    storage = db.get_storage()
    new_assets = []

    for i, upload in enumerate(files):
        if not hasattr(upload, "read"):
            continue
        contents = await upload.read()

        if len(contents) > 5 * 1024 * 1024:
            continue  # skip oversized

        try:
            img = Image.open(io.BytesIO(contents))
            width, height = img.size
        except Exception:
            continue  # skip invalid

        if width == height:
            orientation = "square"
        elif width > height:
            orientation = "landscape"
        else:
            orientation = "portrait"

        label = _auto_label(width, height, len(existing) + i)

        ext = upload.filename.rsplit(".", 1)[-1] if "." in upload.filename else "png"
        storage_path = f"{page_id}/assets/{uuid.uuid4().hex}.{ext}"
        content_type = upload.content_type or "image/png"

        storage.from_(SUPABASE_ASSETS_BUCKET).upload(storage_path, contents, {"content-type": content_type})
        public_url = storage.from_(SUPABASE_ASSETS_BUCKET).get_public_url(storage_path)

        new_assets.append(LabeledAsset(
            url=public_url, label=label,
            width=width, height=height, orientation=orientation,
        ))

    if not new_assets:
        return Response("No valid images uploaded", status_code=400)

    if project.brand_memory is None:
        project.brand_memory = BrandMemory(
            business_name="", website_type="", primary_goal="",
            labeled_assets=new_assets,
        )
    else:
        project.brand_memory.labeled_assets.extend(new_assets)

    db.save_project(project)

    # Return all asset cards (full replace via hx-swap="innerHTML")
    from user_app.frontend.pages.onboarding import render_asset_card
    all_assets = project.brand_memory.labeled_assets
    cards = [render_asset_card(a, page_id) for a in all_assets]
    return Div(*cards)


async def delete_asset(req, page_id: str):
    """Remove an asset from brand_memory and Supabase storage."""
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return Response("Not found", status_code=404)

    url = req.query_params.get("url", "")
    if not url or not project.brand_memory:
        return Response("", status_code=200)

    # Remove from labeled_assets
    project.brand_memory.labeled_assets = [
        a for a in project.brand_memory.labeled_assets if a.url != url
    ]
    db.save_project(project)

    # Try to delete from storage (best-effort)
    try:
        marker = f"/object/public/{SUPABASE_ASSETS_BUCKET}/"
        if marker in url:
            path = url.split(marker, 1)[1]
            db.get_storage().from_(SUPABASE_ASSETS_BUCKET).remove([path])
    except Exception:
        pass

    return Response("", status_code=200)


async def save_memory(req, page_id: str):
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    form = await req.form()

    for field in ("business_name", "website_type", "primary_goal"):
        if not form.get(field, "").strip():
            return error_page(f"{field.replace('_', ' ').title()} is required")

    # Preserve assets uploaded during the wizard
    existing_assets = []
    if project.brand_memory and project.brand_memory.labeled_assets:
        existing_assets = project.brand_memory.labeled_assets

    try:
        memory = BrandMemory(
            business_name=form.get("business_name", ""),
            website_type=form.get("website_type", ""),
            primary_goal=form.get("primary_goal", ""),
            description=form.get("description", ""),
            theme=form.get("theme", "professional"),
            primary_color=form.get("primary_color", "#2563eb"),
            secondary_color=form.get("secondary_color", "#1e40af"),
            contact_email=form.get("contact_email", ""),
            contact_phone=form.get("contact_phone", ""),
            address=form.get("address", ""),
            tagline=form.get("tagline", ""),
            services=[s.strip() for s in form.get("services", "").split(",") if s.strip()],
            project_intent=ProjectIntent(form.get("project_intent", "validation")),
            labeled_assets=existing_assets,
        )
        save_brand_memory(project, memory)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/pages/{page_id}", status_code=303)


# Goal -> (website_type, project_intent) mapping
_GOAL_MAP = {
    "collect_emails":   ("saas",            ProjectIntent.VALIDATION),
    "sell_preorder":    ("digital_product",  ProjectIntent.VALIDATION),
    "schedule_call":    ("local_business",   ProjectIntent.PRESENCE),
    "build_authority":  ("portfolio",        ProjectIntent.PRESENCE),
    "direct_traffic":   ("saas",            ProjectIntent.VALIDATION),
}


def _darken_hex(hex_color: str, factor: float = 0.75) -> str:
    """Darken a hex color by the given factor (0-1). Returns hex string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return "#1e40af"
    r = int(int(hex_color[0:2], 16) * factor)
    g = int(int(hex_color[2:4], 16) * factor)
    b = int(int(hex_color[4:6], 16) * factor)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


async def braindump(req, page_id: str):
    """Brain Dump: collect minimal input, build memory, generate site, redirect to preview."""
    user = req.scope["user"]
    if is_rate_limited(f"braindump:{user.id}", limit=10, window_seconds=3600):
        return rate_limit_response("You've made too many generation requests. Please wait before trying again.")
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    form = await req.form()

    business_name = form.get("business_name", "").strip()
    if not business_name:
        return error_page("Business name is required")

    primary_goal = form.get("primary_goal", "").strip()
    if not primary_goal:
        return error_page("Primary goal is required")

    description = form.get("description", "").strip()

    # Infer website_type and project_intent from goal
    website_type, project_intent = _GOAL_MAP.get(
        primary_goal, ("saas", ProjectIntent.VALIDATION)
    )

    # Derive secondary color from primary
    primary_color = form.get("primary_color", "#4F46E5").strip()
    secondary_color = _darken_hex(primary_color)

    # Preserve any assets already uploaded
    existing_assets = []
    if project.brand_memory and project.brand_memory.labeled_assets:
        existing_assets = project.brand_memory.labeled_assets

    # Read optional personalization fields
    tagline = form.get("tagline", "").strip()
    contact_email = form.get("contact_email", "").strip()
    contact_phone = form.get("contact_phone", "").strip()
    address = form.get("address", "").strip()
    industry = form.get("industry", "").strip()

    memory = BrandMemory(
        business_name=business_name,
        website_type=website_type,
        primary_goal=primary_goal,
        description=description,
        theme=form.get("theme", "professional"),
        primary_color=primary_color,
        secondary_color=secondary_color,
        tagline=tagline,
        contact_email=contact_email,
        contact_phone=contact_phone,
        address=address,
        services=[industry] if industry else [],
        project_intent=project_intent,
        labeled_assets=existing_assets,
    )

    try:
        # DRAFT -> INPUT_READY -> MEMORY_READY
        save_brand_memory(project, memory)
        # MEMORY_READY -> SITE_GENERATED (AI + Jinja2)
        run_generate_and_render(project, user)
        # SITE_GENERATED -> PREVIEW
        move_to_preview(project)
    except CoreError as e:
        # If AI fails, project lands in MEMORY_READY — show_page renders retry page
        pass

    return RedirectResponse(f"/pages/{page_id}", status_code=303)
