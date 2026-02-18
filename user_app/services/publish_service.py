from datetime import datetime, timezone

from core.models.project import Project
from core.models.user import User
from core.state_machine.engine import transition
from core.state_machine.states import ProjectState
from core.publishing.validator import validate_for_publish
from core.publishing.renderer import render_final_page
from core.publishing.storage import upload_site
from core.publishing.urls import get_public_url
from core.billing.trial import calculate_trial_end
from core.errors import CoreError
from config.settings import SUPABASE_STORAGE_BUCKET
from user_app import db


def publish_project(project: Project, user: User) -> str:
    """
    Orchestrate the full publish flow:
    1. Validate state + HTML + CSS
    2. Render final page (inline CSS)
    3. Upload to storage
    4. Record published site
    5. Transition state
    6. Set trial timer
    7. Persist everything

    Returns: public URL
    """
    if project.state != ProjectState.PREVIEW:
        raise CoreError("Project must be in preview state to publish")

    if project.site_version is None:
        raise CoreError("No site version to publish")

    html = project.site_version.html
    css = project.site_version.css
    version = project.site_version.version

    # Strip legacy <script> tags from stored HTML (nav JS is re-injected by render_final_page)
    import re
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)

    # 1. Validate
    validate_for_publish(html, css)

    # 2. Render
    rendered = render_final_page(html, css)

    # 3. Upload
    try:
        storage_client = db.get_storage()
        storage_path = upload_site(storage_client, project.id, version, rendered, SUPABASE_STORAGE_BUCKET)
    except CoreError:
        raise
    except Exception as e:
        raise CoreError(f"Storage upload failed: {e}")

    # 4. Get public URL
    public_url = get_public_url(project.id, version)

    # 5. Record published site
    db.save_published_site(
        project_id=project.id,
        version=version,
        storage_path=storage_path,
        public_url=public_url,
        html_content=html,
        css_content=css,
    )

    # 6. Transition state
    now = datetime.now(timezone.utc)
    project.published_at = now
    project.site_version.is_published = True
    transition(project, ProjectState.PUBLISHED)

    # 7. Persist project
    db.save_project(project)

    # 8. Set trial timer (for free users)
    trial_end = calculate_trial_end(now)
    db.update_project_trial(project.id, trial_end)

    return public_url
