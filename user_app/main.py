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

# --- Routes: Pages ---

@rt("/")
def get(req, sess):
    if sess.get("user_id"):
        return RedirectResponse("/pages", status_code=303)
    return landing_page()


@rt("/dashboard")
def get(req):
    return RedirectResponse("/pages", status_code=303)


@rt("/page")
def get(req):
    return RedirectResponse("/pages", status_code=303)


@rt("/pages")
def get(req):
    return projects.dashboard(req)


@rt("/pages")
async def post(req):
    return projects.create_project(req)


# --- Routes: Profile (top-level) ---

@rt("/profile")
def get(req):
    return projects.show_user_profile(req)


# --- Routes: Project detail ---

@rt("/pages/{page_id}")
async def get(req, page_id: str):
    return await projects.show_project(req, page_id)


@rt("/pages/{page_id}/delete")
async def post(req, page_id: str):
    return await projects.delete_project(req, page_id)


@rt("/pages/{page_id}/memory")
async def post(req, page_id: str):
    return await projects.save_memory(req, page_id)


@rt("/pages/{page_id}/braindump")
async def post(req, page_id: str):
    return await projects.braindump(req, page_id)


@rt("/pages/{page_id}/assets")
async def post(req, page_id: str):
    return await projects.upload_asset(req, page_id)


@rt("/pages/{page_id}/assets")
async def delete(req, page_id: str):
    return await projects.delete_asset(req, page_id)


# --- Routes: Profile & Site detail ---

@rt("/pages/{page_id}/details")
async def get(req, page_id: str):
    return await projects.get_brand_details(req, page_id)


@rt("/pages/{page_id}/site")
async def get(req, page_id: str):
    return await projects.show_site(req, page_id)


# --- Routes: Preview render (iframe) ---

@rt("/pages/{page_id}/preview-render")
async def get(req, page_id: str):
    return await projects.preview_render(req, page_id)


# --- Routes: AI Generation ---

@rt("/pages/{page_id}/plan")
async def post(req, page_id: str):
    return await generation.run_planner(req, page_id)


@rt("/pages/{page_id}/approve")
async def post(req, page_id: str):
    return await generation.approve(req, page_id)


@rt("/pages/{page_id}/generate")
async def post(req, page_id: str):
    return await generation.run_generator(req, page_id)


# --- Routes: Editing ---

@rt("/pages/{page_id}/edit")
async def get(req, page_id: str):
    return await editing.show_edit_page(req, page_id)


@rt("/pages/{page_id}/edit")
async def post(req, page_id: str):
    return await editing.edit_text(req, page_id)


@rt("/pages/{page_id}/edit-content")
async def post(req, page_id: str):
    return await editing.edit_content(req, page_id)


@rt("/pages/{page_id}/edit-image")
async def post(req, page_id: str):
    return await editing.edit_image(req, page_id)


@rt("/pages/{page_id}/bulk-upload")
async def post(req, page_id: str):
    return await editing.bulk_upload_images(req, page_id)


# --- Routes: Publishing ---

@rt("/pages/{page_id}/publish")
async def post(req, page_id: str):
    return await publishing.publish(req, page_id)


@rt("/sites/{page_id}")
async def get(req, page_id: str):
    return await publishing.view_published(req, page_id)


# --- Routes: Billing ---

@rt("/pages/{page_id}/trial")
async def get(req, page_id: str):
    return await billing.trial_status(req, page_id)


@rt("/billing")
async def get(req):
    return await billing.show_billing(req)


@rt("/billing/checkout")
async def post(req):
    return await billing.create_checkout(req)


@rt("/api/webhooks/lemon-squeezy")
async def post(req):
    return await billing.lemon_squeezy_webhook(req)

# --- Routes: Help ---

@rt("/help")
async def get(req):
    return await help_routes.show_help(req)

# --- Start ---

if __name__ == "__main__":
    from config.settings import APP_HOST, APP_PORT
    serve(host=APP_HOST, port=APP_PORT)
