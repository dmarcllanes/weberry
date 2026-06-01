import io
import logging
import uuid

log = logging.getLogger(__name__)

from PIL import Image
from fasthtml.common import RedirectResponse, Response, Div, P

from core.models.brand_memory import BrandMemory, ProjectIntent, LabeledAsset
from core.state_machine.states import ProjectState
from core.billing.trial import days_remaining as trial_days_remaining
from config.settings import SUPABASE_ASSETS_BUCKET
from core.errors import CoreError
from core.raw_template.loader import read_template_html
from user_app import db
from user_app.routes import error_page
from core.billing.entitlements import can_generate_site, next_credit_type
from user_app.middleware.rate_limiter import is_rate_limited, rate_limit_response
from user_app.services.project_service import (
    create_project_for_user,
    get_user_projects,
    save_brand_memory,
    move_to_preview,
)
from user_app.frontend.pages.dashboard import dashboard_page
from user_app.frontend.pages.onboarding import onboarding_page, waiting_for_plan_page
from user_app.frontend.pages.plan_review import plan_review_page
from user_app.frontend.pages.generating import generating_page
from user_app.frontend.pages.preview import preview_page
from user_app.frontend.pages.publish import published_page
from user_app.frontend.pages.profile import user_profile_page, brand_profile_page, brand_info_component
from user_app.frontend.pages.site_detail import site_detail_page
from user_app.frontend.pages.template_picker import template_picker_page


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
    show_new = can_generate_site(user)
    return dashboard_page(user, projects, show_new_button=show_new, active_tab=tab, page=page)


def show_user_profile(req):
    """Top-level /profile — show user account info only."""
    user = req.scope["user"]
    return user_profile_page(user)


def new_page_picker(req):
    """GET /pages/new — show template picker before creating a project."""
    user = req.scope["user"]
    show_new = can_generate_site(user)
    return template_picker_page(user, show_new=show_new)


async def create_page(req):
    """POST /pages — create project then redirect to onboarding, preserving preferred template."""
    user = req.scope["user"]
    form = await req.form()
    preferred_template_id = form.get("preferred_template_id", "").strip() or None
    try:
        project = create_project_for_user(user)
    except CoreError as e:
        return error_page(str(e))
    if preferred_template_id:
        project.template_id = preferred_template_id
        db.save_project(project)
    # Raw-template flow goes to image upload first
    from core.raw_template.loader import get_raw_template
    if preferred_template_id and get_raw_template(preferred_template_id):
        return RedirectResponse(f"/pages/{project.id}/upload", status_code=303)
    return RedirectResponse(f"/pages/{project.id}", status_code=303)


async def show_page(req, page_id: str):
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return error_page("Page not found", 404)

    state = project.state

    # Route to the correct page based on project state
    if state == ProjectState.DRAFT:
        # Raw-template flow: redirect to image upload on first visit (before upload step)
        from core.raw_template.loader import get_raw_template
        if project.template_id and get_raw_template(project.template_id):
            return RedirectResponse(f"/pages/{page_id}/upload", status_code=303)
        return onboarding_page(user, project)

    if state == ProjectState.INPUT_READY:
        return onboarding_page(user, project)

    if state == ProjectState.MEMORY_READY:
        # Raw-template flow: send back to braindump wizard to retry
        from core.raw_template.loader import get_raw_template
        if project.template_id and get_raw_template(project.template_id):
            return onboarding_page(user, project)
        # Legacy Jinja2 flow fallback
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
    import re
    import hashlib
    user = req.scope["user"]
    project = db.get_project(page_id)
    if project is None or project.user_id != user.id:
        return Response("Not found", status_code=404)

    if not project.site_version or not project.site_version.html:
        return Response("<p>No preview available yet.</p>", media_type="text/html")

    html = project.site_version.html
    css = project.site_version.css or ""
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    if css:
        html = html.replace("</head>", f"<style>{css}</style></head>", 1)
    from core.publishing.renderer import inject_nav_js
    html = inject_nav_js(html)

    edit_mode = req.query_params.get("edit") == "1"
    if edit_mode:
        editor_snippet = (
            '<style>:root{'
            '--ob-primary:#2563eb;'
            '--ob-primary-hover:#1d4ed8;'
            '--ob-surface:#0f0f24;'
            '--ob-text:#e2e8f0;'
            '--ob-muted:#64748b;'
            '--ob-border:rgba(37,99,235,.3);'
            '}</style>'
            f'<script>window.__OKENABA_PAGE_ID__="{page_id}";</script>'
            '<script src="/static/js/visual_editor.js"></script>'
        )
        html = html.replace("</body>", editor_snippet + "\n</body>", 1)

    # ETag: skip for edit mode (always fresh); 304 for read-only preview
    if not edit_mode:
        etag = '"' + hashlib.md5(html.encode(), usedforsecurity=False).hexdigest()[:16] + '"'
        if req.headers.get("if-none-match") == etag:
            return Response(status_code=304)
        return Response(html, media_type="text/html", headers={
            "ETag": etag,
            "Cache-Control": "private, no-cache",
        })

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


_COPYRIGHT_RE = __import__("re").compile(
    r"(?:copyright\s*(?:©|&copy;)?\s*\d{4}|©\s*\d{4})[^<]*",
    __import__("re").IGNORECASE,
)
_RIGHTS_RE = __import__("re").compile(
    r"all\s+rights?\s+reserved[^<]*",
    __import__("re").IGNORECASE,
)


def _strip_contact_text(html: str, memory) -> str:
    """Remove contact values, tagline, and copyright lines the AI placed into template text nodes."""
    import re
    vals = [v.strip() for v in [
        getattr(memory, "contact_email", "") or "",
        getattr(memory, "contact_phone", "") or "",
        getattr(memory, "address", "") or "",
        getattr(memory, "tagline", "") or "",
    ] if v.strip()]

    def _clean(m):
        text = m.group(1)
        cleaned = text

        # Remove contact values and tagline
        for v in vals:
            cleaned = cleaned.replace(v, "")

        # Remove copyright / all-rights-reserved lines the AI injected
        cleaned = _COPYRIGHT_RE.sub("", cleaned)
        cleaned = _RIGHTS_RE.sub("", cleaned)

        # Strip leftover separators
        cleaned = re.sub(r"[\s|·•\-–—,/\\]+$", "", cleaned).strip()
        cleaned = re.sub(r"^[\s|·•\-–—,/\\]+", "", cleaned)

        if not cleaned or len(cleaned) < 2:
            return "><"
        return f">{cleaned}<"

    return re.sub(r">([^<>]{2,})<", _clean, html)


def _build_contact_footer(memory, primary_color: str) -> str:
    """Return a polished self-contained contact footer, or '' if no contact info."""
    from datetime import datetime
    email   = (memory.contact_email or "").strip()
    phone   = (memory.contact_phone or "").strip()
    address = (memory.address       or "").strip()
    name    = (memory.business_name or "").strip()

    tagline = (memory.tagline or "").strip()

    if not any([email, phone, address, tagline]):
        return ""

    pc   = primary_color.strip() if primary_color else "#2563eb"
    year = datetime.now().year

    def _hex_to_rgb(h):
        h = h.lstrip("#")
        if len(h) != 6:
            return "37,99,235"
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"

    rgb = _hex_to_rgb(pc)

    def _card(icon: str, label: str, value: str, href: str = "") -> str:
        val_html = (
            f'<a href="{href}" style="color:#f1f5f9;font-size:0.95rem;font-weight:600;'
            f'text-decoration:none;display:block;margin:0;line-height:1.4;word-break:break-word">{value}</a>'
            if href else
            f'<span style="color:#f1f5f9;font-size:0.95rem;font-weight:600;display:block;'
            f'margin:0;line-height:1.4;word-break:break-word">{value}</span>'
        )
        return (
            f'<div style="flex:1;min-width:220px;max-width:300px;'
            f'background:rgba(255,255,255,0.04);'
            f'border:1px solid rgba({rgb},0.25);'
            f'border-radius:1.25rem;padding:1.5rem 1.75rem;'
            f'display:flex;align-items:center;gap:1.25rem;'
            f'box-shadow:0 4px 24px rgba(0,0,0,0.3),inset 0 1px 0 rgba(255,255,255,0.05)">'

            f'<div style="width:52px;height:52px;flex-shrink:0;'
            f'background:rgba({rgb},0.15);'
            f'border:1px solid rgba({rgb},0.35);'
            f'border-radius:1rem;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:1.35rem;'
            f'box-shadow:0 0 16px rgba({rgb},0.2)">'
            f'{icon}</div>'

            f'<div style="min-width:0;flex:1">'
            f'<p style="color:rgba({rgb},0.9);font-size:0.65rem;text-transform:uppercase;'
            f'letter-spacing:0.14em;margin:0 0 0.35rem;font-weight:700">{label}</p>'
            f'{val_html}'
            f'</div></div>'
        )

    cards = []
    if email:
        cards.append(_card("✉", "Email", email, f"mailto:{email}"))
    if phone:
        cards.append(_card("✆", "Phone", phone, f"tel:{phone}"))
    if address:
        cards.append(_card("⊙", "Address", address))

    cards_html   = "\n".join(cards)
    cards_row    = (
        f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:1.25rem;margin-bottom:3rem">'
        f'{cards_html}</div>'
        if cards_html else
        '<div style="margin-bottom:2rem"></div>'
    )
    subtitle     = tagline if tagline else "We'd love to hear from you"
    copyright    = f"© {year} {name}. All rights reserved." if name else f"© {year} All rights reserved."

    return (
        f'\n<section style="'
        f'background:linear-gradient(180deg,#0b0f1a 0%,#080b12 100%);'
        f'padding:4.5rem 2rem 2.5rem;'
        f'font-family:system-ui,-apple-system,BlinkMacSystemFont,sans-serif;'
        f'position:relative;overflow:hidden">'

        # subtle radial glow at top centre
        f'<div style="position:absolute;top:-80px;left:50%;transform:translateX(-50%);'
        f'width:700px;height:260px;'
        f'background:radial-gradient(ellipse,rgba({rgb},0.12) 0%,transparent 70%);'
        f'pointer-events:none"></div>'

        f'<div style="max-width:1000px;margin:0 auto;position:relative">'

        # header
        f'<div style="text-align:center;margin-bottom:3rem">'
        f'<div style="display:inline-flex;align-items:center;gap:0.6rem;'
        f'background:rgba({rgb},0.1);border:1px solid rgba({rgb},0.3);'
        f'border-radius:999px;padding:0.35rem 1.1rem;margin-bottom:1.1rem">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{pc};'
        f'box-shadow:0 0 6px {pc};display:inline-block"></span>'
        f'<span style="color:{pc};font-size:0.68rem;letter-spacing:0.18em;'
        f'text-transform:uppercase;font-weight:700">Contact Us</span>'
        f'</div>'
        f'<h2 style="color:#f1f5f9;font-size:1.9rem;font-weight:800;margin:0 0 0.5rem;'
        f'letter-spacing:-0.02em">Get In Touch</h2>'
        f'<p style="color:#475569;font-size:0.9rem;margin:0">{subtitle}</p>'
        f'</div>'

        f'{cards_row}'

        # gradient divider
        f'<div style="height:1px;'
        f'background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);'
        f'margin-bottom:1.75rem"></div>'

        # copyright
        f'<p style="text-align:center;color:#334155;font-size:0.82rem;margin:0">{copyright}</p>'

        f'</div></section>'
    )


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

    # Check credits before spending an AI call
    if not can_generate_site(user):
        return error_page("You have no credits. Purchase a pack to generate more sites.")

    credit_type = next_credit_type(user)

    from pathlib import Path
    from asyncio import to_thread as _to_thread
    from core.raw_template.loader import get_raw_template
    from core.raw_template.rewriter import rewrite_html
    from core.raw_template.assembler import assemble
    from core.models.site_version import SiteVersion
    from core.state_machine.engine import transition
    from core.state_machine.states import ProjectState as PS

    raw_tpl = get_raw_template(project.template_id or "")
    if not raw_tpl:
        return error_page("Template not found. Please start over and select a template.")

    try:
        # 1. Save brand memory
        save_brand_memory(project, memory)

        # 2. Read original HTML
        html = read_template_html(raw_tpl["html_path"])

        # 3. AI rewrites text content — offloaded to thread so event loop stays free
        rewritten = await _to_thread(rewrite_html, html, memory)

        # 3b. Remove contact info from plain text nodes so it doesn't show raw
        rewritten = _strip_contact_text(rewritten, memory)

        # 4. Build image map from uploaded assets
        image_map: dict[str, str] = {a.label: a.url for a in (memory.labeled_assets or [])}
        log.info("[braindump] %s — image_map keys: %s", page_id, list(image_map.keys()))

        # 5. Inject images + inline CSS/JS → self-contained HTML
        final_html = assemble(
            raw_tpl, rewritten, image_map,
            primary_color=primary_color,
            secondary_color=secondary_color,
        )

        # 6. Inject styled contact footer if any contact info was provided
        contact_html = _build_contact_footer(memory, primary_color)
        if contact_html:
            final_html = final_html.replace("</body>", contact_html + "\n</body>", 1)

        # 7. Store and transition to PREVIEW
        project.site_version = SiteVersion(html=final_html, css="", version=1)
        transition(project, PS.SITE_GENERATED)
        db.save_project(project)
        move_to_preview(project)

    except CoreError as e:
        import logging
        logging.error(f"[braindump] generation failed for {page_id}: {e}")
        return error_page(f"Generation failed: {e}")

    # TESTING MODE — skip credit deduction and trial limits
    # db.deduct_credit(user)
    # from datetime import datetime, timezone, timedelta
    # from config.settings import FREE_CREDIT_TRIAL_DAYS, PAID_CREDIT_TRIAL_DAYS
    # days = FREE_CREDIT_TRIAL_DAYS if credit_type == "free" else PAID_CREDIT_TRIAL_DAYS
    # trial_ends = datetime.now(timezone.utc) + timedelta(days=days)
    # db.update_project_trial(page_id, trial_ends_at=trial_ends)

    return RedirectResponse(f"/pages/{page_id}", status_code=303)
