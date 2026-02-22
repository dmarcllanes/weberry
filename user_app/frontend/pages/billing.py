"""Billing page — payment coming soon."""

from fasthtml.common import Div, H1, H2, P, Span
from user_app.frontend.layout import page_layout


def billing_page(user):
    """Render the billing page (payment disabled during beta)."""

    content = Div(
        H1("Billing & Subscription", cls="step-title", style="margin-bottom:2rem"),
        Div(
            Div(
                Div(
                    H2("Beta Access", style="font-size:1.75rem;margin-bottom:0.5rem"),
                    Span(
                        "Active",
                        cls="state-badge state-badge--published",
                        style="margin-left:0.5rem;vertical-align:middle",
                    ),
                    style="display:flex;align-items:baseline",
                ),
                P(
                    "Unlimited pages & AI generations included",
                    style="color:var(--color-primary);font-weight:600;margin-top:0.25rem",
                ),
                P(
                    "You have full access during the beta. Paid plans will be introduced soon.",
                    style="color:var(--color-text-light);margin-top:0.5rem",
                ),
            ),
            cls="billing-card",
            style=(
                "padding:2rem;"
                "background:var(--color-background);"
                "border:1px solid var(--color-border);"
                "border-radius:var(--radius-lg);"
                "margin-bottom:2rem;"
            ),
        ),
        cls="dashboard-content",
        style="max-width:800px;margin:0 auto",
    )

    return page_layout(content, user=user, title="Okenaba - Billing", active_nav="billing")
