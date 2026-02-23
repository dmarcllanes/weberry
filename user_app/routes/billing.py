from fasthtml.common import Response

from user_app import db
from user_app.routes import json_error


async def trial_status(req, page_id: str):
    user = req.scope["user"]
    row = db.get_project_row(page_id)
    if row is None or row["user_id"] != user.id:
        return json_error("Page not found", 404)

    return {
        "plan": user.plan.value,
        "trial_ends_at": None,
        "is_trial_active": True,
        "is_trial_expired": False,
        "days_remaining": None,
        "is_paused": row.get("is_paused", False),
    }


async def show_billing(req):
    from user_app.frontend.pages.billing import billing_page
    user = req.scope["user"]
    return billing_page(user)


async def create_checkout(req):
    return Response("Payment is not available yet.", status_code=503)


async def lemon_squeezy_webhook(req):
    return Response("Webhook disabled.", status_code=200)
