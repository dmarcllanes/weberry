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
    available   = user.available_credits
    free_active = user.free_credit_active
    days_left   = _days_until(user.free_credits_expires_at) if free_active else 0

    badge = (
        Span("Active",     cls="state-badge state-badge--published")
        if available > 0 else
        Span("No Credits", cls="state-badge state-badge--error")
    )

    notices = []
    if free_active and user.free_credits > 0:
        notices.append(
            Div(
                Safe('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'),
                Span(f"Free credit expires in {days_left} day{'s' if days_left != 1 else ''} — pages generated with it stay live for 7 days."),
                cls="bill-notice bill-notice--warning",
            )
        )
    elif not free_active and user.free_credits > 0:
        notices.append(
            Div(
                Span("Free credit expired. Purchase a pack to generate more pages."),
                cls="bill-notice bill-notice--error",
            )
        )

    return Div(
        Div(
            H2("Credit Balance", cls="bill-section-title"),
            badge,
            cls="bill-card-header",
        ),
        Div(
            _stat_block(str(available),         "Available Credits"),
            Div(cls="bill-stat-divider"),
            _stat_block(str(user.paid_credits),  "Purchased"),
            Div(cls="bill-stat-divider"),
            _stat_block(
                str(user.free_credits) if free_active else "0",
                f"Free ({days_left}d left)" if free_active else "Free (expired)",
            ),
            cls="bill-stats",
        ),
        *notices,
        cls="bill-card",
    )


def _stat_block(value, label):
    return Div(
        Div(value, cls="bill-stat-value"),
        Div(label,  cls="bill-stat-label"),
        cls="bill-stat",
    )


def _pack_card(pack, checkout_enabled=False):
    highlight = pack["highlight"]
    card_cls  = "pack-card pack-card--featured" if highlight else "pack-card"

    badge_el = (
        Span("Most Popular", cls="pack-badge")
        if highlight else
        Div(cls="pack-spacer")
    )

    if checkout_enabled:
        cta = Form(
            Input(type="hidden", name="pack", value=pack["key"]),
            Button(
                f"Buy {pack['credits']} Credits",
                cls="button button-primary" if highlight else "button button-secondary",
                type="submit",
                style="width:100%",
            ),
            method="post", action="/checkout",
            cls="pack-cta",
        )
    else:
        cta = Button(
            "Coming Soon",
            cls="button button-secondary",
            disabled=True,
            style="width:100%;opacity:0.55;cursor:not-allowed",
        )

    return Div(
        badge_el,
        H3(pack["name"], cls="pack-name"),
        P(pack["description"], cls="pack-desc"),
        Div(
            Span(f"${pack['price']}", cls="pack-price-amount"),
            Span(" one-time",         cls="pack-price-period"),
        ),
        Div(
            Span(f"{pack['credits']} credits",     cls="pack-credits-count"),
            Span(f" · ${pack['per_credit']}/credit", cls="pack-credits-rate"),
            style="margin:0.4rem 0 0",
        ),
        Div(
            _check_item("30-day page lifetime per credit"),
            _check_item("AI-powered site generation"),
            _check_item("Custom image editing"),
            _check_item("Credits never expire"),
            cls="pack-features",
        ),
        cta,
        cls=card_cls,
    )


def _check_item(text):
    return Div(
        Safe('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="pack-feature-check"><polyline points="20 6 9 17 4 12"/></svg>'),
        Span(text, cls="pack-feature-check-text"),
        cls="pack-feature",
    )


def _how_credits_work():
    rules = [
        ("1 credit",     "= 1 AI-generated site",         "var(--color-primary)"),
        ("Free signup",  "→ 7-day page lifetime",          "var(--color-warning, #f59e0b)"),
        ("Paid credits", "→ 30-day page lifetime",         "var(--color-success)"),
        ("Credits",      "never expire — use any time",    "var(--color-text-light)"),
    ]
    return Div(
        H3("How credits work", cls="how-credits-title"),
        *[
            Div(
                Span(label, cls="credit-rule-key", style=f"color:{color}"),
                Span(f" {desc}"),
                cls="credit-rule",
            )
            for label, desc, color in rules
        ],
        cls="how-credits",
    )


def billing_page(user, checkout_enabled=False):
    content = Div(
        H1("Credits", cls="step-title"),
        _credit_balance_card(user),
        H2("Buy Credits", cls="bill-subsection-title"),
        Div(
            *[_pack_card(p, checkout_enabled) for p in _CREDIT_PACKS],
            cls="pack-cards",
        ),
        _how_credits_work(),
        cls="help-content",
    )

    return page_layout(content, user=user, title="Okenaba - Credits", active_nav="billing")
