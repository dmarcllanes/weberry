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


async def create_checkout(req):
    user = req.scope["user"]
    try:
        body = await req.json()
    except Exception:
        body = dict(await req.form())
    
    plan_type = body.get("plan_type")
    if not plan_type:
        return json_error("Missing plan_type", 400)

    from core.billing.lemon_squeezy import create_checkout_url
    
    # Construct redirect URL based on request host
    scheme = req.url.scheme
    host = req.headers.get("host", "localhost:5001")
    redirect_url = f"{scheme}://{host}/billing?success=1"

    try:
        url = create_checkout_url(user.email, plan_type, redirect_url)
    except ValueError as e:
        return json_error(str(e), 400)
    except Exception as e:
        print(f"Error creating checkout: {e}")
        return json_error("Failed to create checkout", 500)

    from fasthtml.common import RedirectResponse
    return RedirectResponse(url, status_code=303)


async def lemon_squeezy_webhook(req):
    from core.billing.lemon_squeezy import verify_webhook_signature
    
    signature = req.headers.get("X-Signature")
    if not signature:
        return Response("Missing signature", status_code=401)

    body = await req.body()
    if not verify_webhook_signature(body, signature):
        return Response("Invalid signature", status_code=401)

    import json
    data = json.loads(body)
    
    event_name = data.get("meta", {}).get("event_name")
    payload = data.get("data", {}).get("attributes", {})
    
    # We need the user's email to match them in our DB
    # 'checkout_data' usually contains 'email' or 'custom' fields
    # In 'subscription_created', it's often in attributes directly or related
    
    # For now, let's look for user_email in custom data if we sent it
    # custom_data = data.get("meta", {}).get("custom_data", {})
    # user_email = custom_data.get("user_email")
    
    # Or from the attributes
    user_email = payload.get("user_email")
    
    if not user_email:
        return Response("No email in webhook", status_code=200) # 200 to acknowledge receipt

    user = db.get_user_by_email(user_email)
    if not user:
        return Response("User not found", status_code=200)

    from user_app.db import update_user_subscription
    
    if event_name in ("subscription_created", "subscription_updated"):
        # Map variant ID to PlanType
        variant_id = str(payload.get("variant_id"))
        from config.settings import LEMON_SQUEEZY_VARIANTS
        
        # Reverse lookup plan from variant ID
        plan = "DRAFTER" # Default
        for p, vid in LEMON_SQUEEZY_VARIANTS.items():
            if str(vid) == variant_id:
                plan = p
                break
        
        status = payload.get("status")
        customer_id = str(payload.get("customer_id"))
        subscription_id = str(data.get("data", {}).get("id")) # Subscription ID is the ID of the data object
        
        db.update_user_subscription(
            user.id,
            plan,
            customer_id,
            subscription_id,
            status,
            variant_id
        )

    elif event_name == "subscription_cancelled":
        # Downgrade to free? Or just mark status?
        # For now, let's keep them on the plan but mark status as cancelled
        # If 'ends_at' is in the past, maybe downgrade.
        # Simple logic: just update status.
        status = payload.get("status")
        customer_id = str(payload.get("customer_id"))
        subscription_id = str(data.get("data", {}).get("id"))
        
        # If cancelled, they might still have access until period ends.
        # We rely on 'status' field in DB for logic.
        
        db.update_user_subscription(
            user.id,
            user.plan.value, # Keep current plan enum
            customer_id,
            subscription_id,
            status,
            str(payload.get("variant_id"))
        )

    return Response("Webhook processed", status_code=200)
