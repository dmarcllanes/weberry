"""Billing page — credit-based model."""

from datetime import datetime, timezone
from fasthtml.common import Div, H1, H2, H3, P, Span, A, Form, Button, Input, Safe

from user_app.frontend.layout import page_layout


_CREDIT_PACKS = [
    {
        "key":         "starter",
        "name":        "Starter",
        "credits":     5,
        "price":       9,
        "per_credit":  "1.80",
        "highlight":   False,
        "description": "Perfect for validating your first ideas.",
    },
    {
        "key":         "growth",
        "name":        "Growth",
        "credits":     15,
        "price":       19,
        "per_credit":  "1.27",
        "highlight":   True,
        "description": "Best value for active builders.",
    },
    {
        "key":         "studio",
        "name":        "Studio",
        "credits":     50,
        "price":       49,
        "per_credit":  "0.98",
        "highlight":   False,
        "description": "High volume — for agencies and prolific founders.",
    },
]


def _days_until(dt: datetime) -> int:
    if dt is None:
        return 0
    delta = dt - datetime.now(timezone.utc)
    if delta.total_seconds() <= 0:
        return 0
    return delta.days + (1 if delta.seconds > 0 else 0)


def _credit_balance_card(user):
    available = user.available_credits
    free_active = user.free_credit_active
    days_left = _days_until(user.free_credits_expires_at) if free_active else 0

    # Badge
    if available > 0:
        badge = Span("Active", cls="state-badge state-badge--published")
    else:
        badge = Span("No Credits", cls="state-badge state-badge--error")

    # Free credit notice
    notices = []
    if free_active and user.free_credits > 0:
        notices.append(
            Div(
                Safe(f"""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>"""),
                Span(f"Free credit expires in {days_left} day{'s' if days_left != 1 else ''} — pages generated with it stay live for 7 days."),
                style=(
                    "display:flex;gap:0.5rem;align-items:flex-start;"
                    "background:#FEF3C7;border:1px solid #FCD34D;"
                    "color:#92400E;border-radius:var(--radius-md);"
                    "padding:0.75rem 1rem;font-size:0.875rem;margin-top:1rem"
                )
            )
        )
    elif not free_active and user.free_credits > 0:
        notices.append(
            Div(
                Span("Free credit expired. Purchase a pack to generate more pages."),
                style=(
                    "background:#FEF2F2;border:1px solid #FECACA;"
                    "color:#991B1B;border-radius:var(--radius-md);"
                    "padding:0.75rem 1rem;font-size:0.875rem;margin-top:1rem"
                )
            )
        )

    return Div(
        # Header row
        Div(
            Div(
                H2("Credit Balance", style="font-size:1.25rem;font-weight:700;margin:0"),
                badge,
                style="display:flex;align-items:center;gap:0.75rem"
            ),
        ),
        # Stats row
        Div(
            _stat_block(str(available), "Available Credits"),
            _divider_v(),
            _stat_block(str(user.paid_credits), "Purchased"),
            _divider_v(),
            _stat_block(
                str(user.free_credits) if free_active else "0",
                f"Free ({days_left}d left)" if free_active else "Free (expired)"
            ),
            style=(
                "display:flex;gap:0;margin-top:1.5rem;"
                "background:var(--color-background-alt);"
                "border:1px solid var(--color-border);"
                "border-radius:var(--radius-lg);overflow:hidden"
            )
        ),
        *notices,
        style=(
            "padding:1.75rem 2rem;"
            "background:var(--color-background);"
            "border:1px solid var(--color-border);"
            "border-radius:var(--radius-lg);"
            "margin-bottom:2rem"
        )
    )


def _stat_block(value, label):
    return Div(
        Div(value, style="font-size:1.75rem;font-weight:700;color:var(--color-text)"),
        Div(label, style="font-size:0.75rem;color:var(--color-text-light);margin-top:0.25rem"),
        style="flex:1;padding:1.25rem 1.5rem;text-align:center"
    )


def _divider_v():
    return Div(style="width:1px;background:var(--color-border);align-self:stretch")


def _pack_card(pack, checkout_enabled=False):
    highlight = pack["highlight"]

    border = "2px solid var(--color-primary)" if highlight else "1px solid var(--color-border)"
    bg = "var(--color-background)" if not highlight else "var(--color-background)"
    shadow = "var(--color-shadow-lg)" if highlight else "var(--color-shadow)"

    popular_badge = (
        Div(
            "Most Popular",
            style=(
                "background:var(--color-primary);color:#fff;"
                "font-size:0.7rem;font-weight:700;letter-spacing:0.05em;"
                "padding:0.25rem 0.75rem;border-radius:9999px;text-align:center;"
                "margin-bottom:1rem;display:inline-block"
            )
        ) if highlight else Div(style="height:1.75rem;margin-bottom:1rem")
    )

    if checkout_enabled:
        cta = Form(
            Input(type="hidden", name="pack", value=pack["key"]),
            Button(
                f"Buy {pack['credits']} Credits",
                cls="button button-primary" if highlight else "btn btn-outline",
                type="submit",
                style="width:100%;font-size:0.9rem"
            ),
            method="post", action="/checkout",
            style="margin-top:auto"
        )
    else:
        cta = Button(
            "Coming Soon",
            cls="button button-primary" if highlight else "btn btn-outline",
            disabled=True,
            style="width:100%;font-size:0.9rem;opacity:0.6;cursor:not-allowed;margin-top:auto"
        )

    return Div(
        popular_badge,
        H3(pack["name"], style="font-size:1.1rem;font-weight:700;margin-bottom:0.25rem"),
        P(pack["description"], style="font-size:0.85rem;color:var(--color-text-light);margin-bottom:1.5rem"),
        # Price
        Div(
            Span(f"${pack['price']}", style="font-size:2rem;font-weight:800;color:var(--color-text)"),
            Span(" one-time", style="font-size:0.8rem;color:var(--color-text-light);margin-left:0.25rem"),
            style="margin-bottom:0.5rem"
        ),
        # Credits
        Div(
            Span(
                f"{pack['credits']} credits",
                style="font-size:0.9rem;font-weight:600;color:var(--color-primary)"
            ),
            Span(
                f" · ${pack['per_credit']}/credit",
                style="font-size:0.8rem;color:var(--color-text-lighter)"
            ),
            style="margin-bottom:1.5rem"
        ),
        # What's included
        _check_item("30-day page lifetime per credit"),
        _check_item("AI-powered site generation"),
        _check_item("Custom image editing"),
        _check_item("Credits never expire"),
        cta,
        style=(
            f"padding:1.5rem;border:{border};border-radius:var(--radius-lg);"
            f"background:{bg};box-shadow:{shadow};"
            "display:flex;flex-direction:column;flex:1"
        )
    )


def _check_item(text):
    return Div(
        Safe("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--color-success);flex-shrink:0;margin-top:1px"><polyline points="20 6 9 17 4 12"/></svg>"""),
        Span(text, style="font-size:0.85rem;color:var(--color-text-light)"),
        style="display:flex;gap:0.5rem;align-items:flex-start;margin-bottom:0.5rem"
    )


def _how_it_works():
    steps = [
        ("1 credit", "= 1 generated site", "var(--color-primary)"),
        ("Free signup", "7-day page lifetime", "#D97706"),
        ("Paid credits", "30-day page lifetime", "var(--color-success)"),
        ("Credits", "never expire", "var(--color-text-light)"),
    ]
    return Div(
        H3("How credits work", style="font-size:1rem;font-weight:700;margin-bottom:1rem;color:var(--color-text)"),
        Div(
            *[
                Div(
                    Span(label, style=f"font-weight:700;color:{color}"),
                    Span(f" {desc}", style="color:var(--color-text-light)"),
                    style="font-size:0.875rem;padding:0.4rem 0;border-bottom:1px solid var(--color-border)"
                )
                for label, desc, color in steps
            ],
            style="display:flex;flex-direction:column"
        ),
        style=(
            "padding:1.5rem;"
            "background:var(--color-background-alt);"
            "border:1px solid var(--color-border);"
            "border-radius:var(--radius-lg);"
            "margin-top:2rem"
        )
    )


def billing_page(user, checkout_enabled=False):
    content = Div(
        H1("Credits", cls="step-title", style="margin-bottom:2rem"),
        _credit_balance_card(user),
        H2("Buy Credits", style="font-size:1.1rem;font-weight:700;margin-bottom:1.25rem;color:var(--color-text)"),
        Div(
            *[_pack_card(p, checkout_enabled) for p in _CREDIT_PACKS],
            style="display:flex;gap:1.25rem;align-items:stretch"
        ),
        _how_it_works(),
        cls="dashboard-content",
        style="max-width:860px;margin:0 auto"
    )

    return page_layout(content, user=user, title="Okenaba - Credits", active_nav="billing")
