"""Billing page — subscription management."""

from fasthtml.common import Div, H1, H2, H3, P, A, Section, Button, Span, Table, Thead, Tbody, Tr, Th, Td, Form, Input
from user_app.frontend.layout import page_layout

def billing_page(user):
    """Render the billing dashboard."""
    
    # Plan Details
    plan_details = {
        "small": {"limit": 10, "price": "$10"},
        "medium": {"limit": 40, "price": "$30"},
        "big": {"limit": 100, "price": "$80"}
    }
    
    current_plan = user.plan.value.lower() if user.plan else "free"
    # Default to small if plan not found or is free/starter
    if current_plan not in plan_details:
        current_plan = "small" # Fallback/Default
        
    plan_info = plan_details.get(current_plan, plan_details["small"])
    page_limit = plan_info["limit"]
    price = plan_info["price"]

    plan_name = current_plan.title()
    
    # Determine status
    if user.subscription_status == "active":
        status = "Active"
        badge_cls = "state-badge state-badge--published"
        sub_text = "Standard Subscription"
    elif user.lemon_squeezy_customer_id:
        status = user.subscription_status.title() if user.subscription_status else "Inactive"
        badge_cls = "state-badge"
        sub_text = "Subscription Paused/Cancelled"
    else:
        # Check trial
        from core.billing.trial import is_trial_active, days_remaining
        # We assume if no subscription, maybe trial? 
        # But we don't have project context here easily without fetching.
        # Let's fallback to "Free Plan" for now if no active sub.
        # Ideally we'd show trial status if we knew it.
        status = "Free Plan"
        badge_cls = "state-badge"
        sub_text = "Upgrade to remove limits"

    # Current Plan Card
    plan_card = Div(
        Div(
            H2("Current Plan", style="font-size:1.1rem;margin-bottom:0.5rem;color:var(--color-text-light)"),
            Div(
                H3(plan_name, style="font-size:1.75rem;margin-bottom:0.25rem"),
                Span(status, cls=badge_cls, style="margin-left:0.5rem;vertical-align:middle"),
                style="display:flex;align-items:baseline"
            ),
             P(f"{page_limit} Pages included", style="color:var(--color-primary);font-weight:600;margin-top:0.25rem"),
            P(sub_text, style="color:var(--color-text-light);margin-top:0.5rem"),
            style="flex:1"
        ),
        Div(
            # Forms
            _checkout_form("MEDIUM", "Upgrade to Medium ($30)") if current_plan in ("small", "free", "drafter") else None,
            _checkout_form("BIG", "Upgrade to Big ($80)") if current_plan != "big" else None,
            
             Button("Manage Subscription", cls="btn btn-outline", onclick="window.location.href='#'") if user.subscription_status == "active" else None,
             
            style="display:flex;flex-direction:column;gap:0.5rem;min-width:200px"
        ),
        cls="billing-card",
        style="display:flex;justify-content:space-between;align-items:flex-start;padding:2rem;background:var(--color-background);border:1px solid var(--color-border);border-radius:var(--radius-lg);margin-bottom:2rem;flex-wrap:wrap;gap:1.5rem"
    )

    # Payment Method - Disabled for LS
    # payment_card = Div(...)

    # Invoices - Disabled for LS
    # invoices = Section(...)
    
    content = Div(
        H1("Billing & Subscription", cls="step-title", style="margin-bottom:2rem"),
        plan_card,
        # payment_card,
        # invoices,
        cls="dashboard-content",
        style="max-width:800px;margin:0 auto"
    )

    return page_layout(content, user=user, title="Okenaba - Billing", active_nav="billing")


def _checkout_form(plan_type, label):
    return Form(
        Input(type="hidden", name="plan_type", value=plan_type),
        Button(label, cls="button button-primary", style="width:100%"),
        method="post", action="/billing/checkout",
        style="margin-bottom:0.5rem"
    )


def _invoice_row(date, amount, status):
    return Tr(
        Td(date, style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(amount, style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(Span(status, cls="state-badge state-badge--published"), style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(A("Download", href="#", style="color:var(--color-primary);text-decoration:none"), style="text-align:right;padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
    )
