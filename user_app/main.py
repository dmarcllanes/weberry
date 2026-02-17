"""
Okenaba — FastHTML app entry point.
Start with: python user_app/main.py
"""

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fasthtml.common import fast_app, serve, Beforeware, RedirectResponse
from starlette.responses import JSONResponse

from user_app.auth.guards import auth_beforeware
from user_app.auth.login import get_or_create_user
from user_app.frontend.pages.login import login_page
from user_app.frontend.pages.landing import landing_page
from user_app.routes import projects, generation, editing, publishing, billing
from user_app.routes import help as help_routes

# --- Beforeware ---

bw = Beforeware(
    auth_beforeware,
    skip=[
        r'^/$',
        r'/favicon\.ico',
        r'/static/.*',
        r'/sites/.*',
        r'/landing',
        r'/login',
        r'/api/auth/.*',
        r'/logout',
        r'/sw.js',
    ],
)

# --- App ---

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

SECRET_KEY = os.environ.get("SESSION_SECRET", "okenaba-dev-secret-change-me")

app, rt = fast_app(
    before=bw,
    static_path=PROJECT_ROOT,
    secret_key=SECRET_KEY,
    pico=False,
)

# --- Routes: Auth ---

@rt("/login")
def get(req):
    return login_page()


@rt("/api/auth/session")
async def post(req, sess):
    try:
        body = await req.json()
    except Exception:
        body = dict(await req.form())
    user_id = body.get("user_id")
    email = body.get("email")
    full_name = body.get("full_name")
    avatar_url = body.get("avatar_url")
    if not user_id or not email:
        return JSONResponse({"error": "missing user_id or email"}, status_code=400)

    get_or_create_user(user_id, email, full_name, avatar_url)
    sess["user_id"] = user_id
    if avatar_url:
        sess["avatar_url"] = avatar_url
    return JSONResponse({"status": "success"})


@rt("/logout")
async def post(req, sess):
    sess.clear()
    return RedirectResponse("/?logged_out=1", status_code=303)


# --- Routes: Landing page (public, no auth) ---
# TODO: Import and wire up your landing page here.

# --- Routes: Projects ---

@rt("/")
def get(req, sess):
    if sess.get("user_id"):
        return RedirectResponse("/projects", status_code=303)
    return landing_page()


@rt("/dashboard")
def get(req):
    return RedirectResponse("/projects", status_code=303)


@rt("/project")
def get(req):
    return RedirectResponse("/projects", status_code=303)


@rt("/projects")
def get(req):
    return projects.dashboard(req)


@rt("/projects")
async def post(req):
    return projects.create_project(req)


# --- Routes: Profile (top-level) ---

@rt("/profile")
def get(req):
    return projects.show_user_profile(req)


# --- Routes: Project detail ---

@rt("/projects/{project_id}")
async def get(req, project_id: str):
    return await projects.show_project(req, project_id)


@rt("/projects/{project_id}/delete")
async def post(req, project_id: str):
    return await projects.delete_project(req, project_id)


@rt("/projects/{project_id}/memory")
async def post(req, project_id: str):
    return await projects.save_memory(req, project_id)


@rt("/projects/{project_id}/braindump")
async def post(req, project_id: str):
    return await projects.braindump(req, project_id)


@rt("/projects/{project_id}/assets")
async def post(req, project_id: str):
    return await projects.upload_asset(req, project_id)


@rt("/projects/{project_id}/assets")
async def delete(req, project_id: str):
    return await projects.delete_asset(req, project_id)


# --- Routes: Profile & Site detail ---

@rt("/projects/{project_id}/details")
async def get(req, project_id: str):
    return await projects.get_brand_details(req, project_id)


@rt("/projects/{project_id}/site")
async def get(req, project_id: str):
    return await projects.show_site(req, project_id)


# --- Routes: Preview render (iframe) ---

@rt("/projects/{project_id}/preview-render")
async def get(req, project_id: str):
    return await projects.preview_render(req, project_id)


# --- Routes: AI Generation ---

@rt("/projects/{project_id}/plan")
async def post(req, project_id: str):
    return await generation.run_planner(req, project_id)


@rt("/projects/{project_id}/approve")
async def post(req, project_id: str):
    return await generation.approve(req, project_id)


@rt("/projects/{project_id}/generate")
async def post(req, project_id: str):
    return await generation.run_generator(req, project_id)


# --- Routes: Editing ---

@rt("/projects/{project_id}/edit")
async def get(req, project_id: str):
    return await editing.show_edit_page(req, project_id)


@rt("/projects/{project_id}/edit")
async def post(req, project_id: str):
    return await editing.edit_text(req, project_id)


@rt("/projects/{project_id}/edit-content")
async def post(req, project_id: str):
    return await editing.edit_content(req, project_id)


@rt("/projects/{project_id}/edit-image")
async def post(req, project_id: str):
    return await editing.edit_image(req, project_id)


# --- Routes: Publishing ---

@rt("/projects/{project_id}/publish")
async def post(req, project_id: str):
    return await publishing.publish(req, project_id)


@rt("/sites/{project_id}")
async def get(req, project_id: str):
    return await publishing.view_published(req, project_id)


# --- Routes: Billing ---

@rt("/projects/{project_id}/trial")
async def get(req, project_id: str):
    return await billing.trial_status(req, project_id)


@rt("/billing")
async def get(req):
    return await billing.show_billing(req)

# --- Routes: Help ---

@rt("/help")
async def get(req):
    return await help_routes.show_help(req)

# --- Start ---

if __name__ == "__main__":
    from config.settings import APP_HOST, APP_PORT
    serve(host=APP_HOST, port=APP_PORT)
