from fasthtml.common import RedirectResponse, Response

from core.errors import CoreError
from core.publishing.pauser import should_pause_site, get_paused_html
from user_app import db
from user_app.routes import error_page
from user_app.services.publish_service import publish_project


async def publish(req, project_id: str):
    user = req.scope["user"]
    project = db.get_project(project_id)
    if project is None or project.user_id != user.id:
        return error_page("Project not found", 404)

    try:
        public_url = publish_project(project, user)
    except CoreError as e:
        return error_page(str(e))

    return RedirectResponse(f"/projects/{project_id}", status_code=303)


async def view_published(req, project_id: str):
    """Serve the published site. Enforces trial on every request."""
    row = db.get_project_row(project_id)
    if row is None:
        return Response("Not found", status_code=404)

    if row["state"] != "published":
        return Response("Site not published", status_code=404)

    # Trial enforcement
    user = db.get_user(row["user_id"])
    trial_ends_at = None
    if row.get("trial_ends_at"):
        from datetime import datetime
        trial_ends_at = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]

    if should_pause_site(user.plan, trial_ends_at):
        if not row.get("is_paused"):
            db.set_project_paused(project_id, True)
        project = db.get_project(project_id)
        name = project.brand_memory.business_name if project and project.brand_memory else ""
        return Response(get_paused_html(name), media_type="text/html")

    # Serve the published site
    published = db.get_latest_published_site(project_id)
    if published is None:
        return Response("Published site not found", status_code=404)

    return RedirectResponse(published["public_url"], status_code=302)
