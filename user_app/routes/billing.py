from fasthtml.common import Response

from core.billing.trial import is_trial_active, is_trial_expired, days_remaining
from user_app import db
from user_app.routes import json_error


async def trial_status(req, project_id: str):
    user = req.scope["user"]
    row = db.get_project_row(project_id)
    if row is None or row["user_id"] != user.id:
        return json_error("Project not found", 404)

    trial_ends_at = None
    if row.get("trial_ends_at"):
        from datetime import datetime
        trial_ends_at = datetime.fromisoformat(row["trial_ends_at"]) if isinstance(row["trial_ends_at"], str) else row["trial_ends_at"]

    return {
        "plan": user.plan.value,
        "trial_ends_at": row.get("trial_ends_at"),
        "is_trial_active": is_trial_active(trial_ends_at),
        "is_trial_expired": is_trial_expired(trial_ends_at),
        "days_remaining": days_remaining(trial_ends_at),
        "is_paused": row.get("is_paused", False),
    }


async def show_billing(req):
    from user_app.frontend.pages.billing import billing_page
    user = req.scope["user"]
    return billing_page(user)
