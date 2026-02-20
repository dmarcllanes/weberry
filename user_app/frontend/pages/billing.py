"""Billing page — subscription management."""

from fasthtml.common import Div, H1, H2, H3, P, A, Section, Button, Span, Table, Thead, Tbody, Tr, Th, Td
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
    status = "Active"
    renewal_date = "Oct 24, 2026"
    amount = f"{price}.00"

    # Current Plan Card
    plan_card = Div(
        Div(
            H2("Current Plan", style="font-size:1.1rem;margin-bottom:0.5rem;color:var(--color-text-light)"),
            Div(
                H3(plan_name, style="font-size:1.75rem;margin-bottom:0.25rem"),
                Span(status, cls="state-badge state-badge--published", style="margin-left:0.5rem;vertical-align:middle"),
                style="display:flex;align-items:baseline"
            ),
             P(f"{page_limit} Pages included", style="color:var(--color-primary);font-weight:600;margin-top:0.25rem"),
            P(f"Renews on {renewal_date} for {amount}/month", style="color:var(--color-text-light);margin-top:0.5rem"),
            style="flex:1"
        ),
        Div(
            Button("Upgrade Plan", cls="button button-primary"),
            Button("Cancel Subscription", cls="btn btn-outline", style="margin-top:0.5rem;width:100%"),
            style="display:flex;flex-direction:column;gap:0.5rem;min-width:160px"
        ),
        cls="billing-card",
        style="display:flex;justify-content:space-between;align-items:flex-start;padding:2rem;background:var(--color-background);border:1px solid var(--color-border);border-radius:var(--radius-lg);margin-bottom:2rem;flex-wrap:wrap;gap:1.5rem"
    )

    # Payment Method
    payment_card = Div(
        H2("Payment Method", style="font-size:1.1rem;margin-bottom:1rem"),
        Div(
            Div(
                Span("💳", style="font-size:1.5rem;margin-right:1rem"),
                Div(
                    P("Visa ending in 4242", style="font-weight:600"),
                    P("Expires 12/28", style="color:var(--color-text-light);font-size:0.9rem"),
                ),
                style="display:flex;align-items:center"
            ),
            Button("Update", cls="btn btn-outline btn-sm"),
            style="display:flex;justify-content:space-between;align-items:center;padding:1rem;border:1px solid var(--color-border);border-radius:var(--radius-md)"
        ),
        cls="billing-section",
        style="margin-bottom:2rem"
    )

    # Invoices
    invoices = Section(
        H2("Invoice History", style="font-size:1.1rem;margin-bottom:1rem"),
        Table(
            Thead(
                Tr(
                    Th("Date", style="text-align:left;padding:0.75rem 0.5rem"),
                    Th("Amount", style="text-align:left;padding:0.75rem 0.5rem"),
                    Th("Status", style="text-align:left;padding:0.75rem 0.5rem"),
                    Th("", style="text-align:right"),
                ),
                style="border-bottom:1px solid var(--color-border)"
            ),
            Tbody(
                _invoice_row("Oct 24, 2026", "$0.00", "Paid"),
                _invoice_row("Sep 24, 2026", "$0.00", "Paid"),
                _invoice_row("Aug 24, 2026", "$0.00", "Paid"),
            ),
            style="width:100%;border-collapse:collapse"
        ),
        cls="billing-section"
    )

    content = Div(
        H1("Billing & Subscription", cls="step-title", style="margin-bottom:2rem"),
        plan_card,
        payment_card,
        invoices,
        cls="dashboard-content",
        style="max-width:800px;margin:0 auto"
    )

    return page_layout(content, user=user, title="Okenaba - Billing", active_nav="billing")


def _invoice_row(date, amount, status):
    return Tr(
        Td(date, style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(amount, style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(Span(status, cls="state-badge state-badge--published"), style="padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
        Td(A("Download", href="#", style="color:var(--color-primary);text-decoration:none"), style="text-align:right;padding:1rem 0.5rem;border-bottom:1px solid var(--color-border)"),
    )
