"""
Okenaba — FastHTML app entry point.
Start with: python user_app/main.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fasthtml.common import fast_app, serve, Beforeware

from user_app.auth.guards import auth_beforeware
from user_app.routes import projects, generation, editing, publishing, billing

# --- Beforeware ---

bw = Beforeware(
    auth_beforeware,
    skip=[r'/favicon\.ico', r'/static/.*', r'/sites/.*', r'/landing'],
)

# --- App ---

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
app, rt = fast_app(before=bw, static_path=PROJECT_ROOT)

# --- Routes: Landing page (public, no auth) ---
# TODO: Import and wire up your landing page here.
#   from user_app.frontend.pages.landing import landing_page
#
#   @rt("/landing")
#   def get(req):
#       return landing_page()

# --- Routes: Dashboard ---

@rt("/")
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


# --- Routes: Profile & Site detail ---

@rt("/projects/{project_id}/profile")
async def get(req, project_id: str):
    return await projects.show_profile(req, project_id)


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


# --- Start ---

if __name__ == "__main__":
    from config.settings import APP_HOST, APP_PORT
    serve(host=APP_HOST, port=APP_PORT)
