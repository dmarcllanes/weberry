from fasthtml.common import RedirectResponse, Response

from core.models.brand_memory import BrandMemory
from core.state_machine.states import ProjectState
from core.billing.trial import days_remaining as trial_days_remaining
from core.errors import CoreError
from user_app import db
from user_app.routes import error_page
from user_app.services.project_service import (
    create_project_for_user,
    get_user_projects,
    save_brand_memory,
)
from user_app.frontend.pages.dashboard import dashboard_page
from user_app.frontend.pages.onboarding import onboarding_page, waiting_for_plan_page
from user_app.frontend.pages.plan_review import plan_review_page
from user_app.frontend.pages.generating import generating_page
from user_app.frontend.pages.preview import preview_page
from user_app.frontend.pages.publish import published_page
from user_app.frontend.pages.profile import profile_page
from user_app.frontend.pages.site_detail import site_detail_page


def dashboard(req):
    user = req.scope["user"]
    projects = get_user_projects(user)
    if len(projects) == 1:
        return RedirectResponse(f"/projects/{projects[0].id}", status_code=303)
    return dashboard_page(user, projects)


def create_project(req):
    user = req.scope["user"]
    try:
        project = create_project_for_user(user)
    except CoreError as e:
        return error_page(str(e))
    return RedirectResponse(f"/projects/{project.id}", status_code=303)


async def show_project(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    state = project.state

    # Route to the correct page based on project state
    if state in (ProjectState.DRAFT, ProjectState.INPUT_READY):
        return onboarding_page(project)

    if state == ProjectState.MEMORY_READY:
        return waiting_for_plan_page(project)

    if state == ProjectState.PLAN_READY:
        return plan_review_page(project)

    if state == ProjectState.PLAN_APPROVED:
        return generating_page(project)

    if state in (ProjectState.SITE_GENERATED, ProjectState.PREVIEW):
        return preview_page(project)

    if state == ProjectState.PUBLISHED:
        pub = db.get_latest_published_site(project_id)
        public_url = pub["public_url"] if pub else ""
        row = db.get_project_row(project_id)
        trial_info = None
        if row and row.get("trial_ends_at"):
            from datetime import datetime
            trial_ends = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]
            trial_info = {"days_remaining": trial_days_remaining(trial_ends)}
        return published_page(project, public_url, trial_info)

    return error_page("Unknown project state")


async def preview_render(req, project_id: str):
    """Serve the generated HTML for the preview iframe."""
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return Response("Not found", status_code=404)

    if not project.site_version or not project.site_version.html:
        return Response("<p>No preview available yet.</p>", media_type="text/html")

    html = project.site_version.html
    css = project.site_version.css or ""
    if css:
        html = html.replace("</head>", f"<style>{css}</style></head>", 1)
    return Response(html, media_type="text/html")


async def show_profile(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)
    return profile_page(project)


async def show_site(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    public_url = None
    trial_info = None
    if project.state == ProjectState.PUBLISHED:
        pub = db.get_latest_published_site(project_id)
        public_url = pub["public_url"] if pub else None
        row = db.get_project_row(project_id)
        if row and row.get("trial_ends_at"):
            from datetime import datetime
            trial_ends = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]
            trial_info = {"days_remaining": trial_days_remaining(trial_ends)}

    return site_detail_page(project, public_url, trial_info)


async def save_memory(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    form = await req.form()

    for field in ("business_name", "website_type", "primary_goal"):
        if not form.get(field, "").strip():
            return error_page(f"{field.replace('_', ' ').title()} is required")

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
        )
        save_brand_memory(project, memory)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/projects/{project_id}", status_code=303)
