"""Profile page — shows and allows editing of brand memory info."""

from fasthtml.common import (
    Div, H1, H2, P, Form, Button, Input, Textarea, Label, Span,
    Section, A, Select, Option,
)

from user_app.frontend.layout import page_layout


def profile_page(project):
    """Display the user's website profile information with edit capability."""
    pid = project.id
    mem = project.brand_memory
    state = project.state.value

    if not mem:
        content = Section(
            Div(
                H1("Profile", cls="step-title"),
                P("No profile information yet. Complete the onboarding first.",
                  cls="step-description"),
                A("Go to Setup", href=f"/projects/{pid}", cls="button button-primary",
                  style="max-width:300px;display:inline-block"),
                cls="step-content",
            ),
            cls="step",
        )
        return page_layout(content, title="Okenaba - Profile", project_id=pid, active_nav="profile")

    # Display card
    info_card = Div(
        Div(
            Div(
                Span(mem.business_name[0].upper() if mem.business_name else "?", cls="profile-avatar-letter"),
                cls="profile-avatar",
            ),
            Div(
                H1(mem.business_name, cls="profile-name"),
                P(mem.tagline, cls="profile-tagline") if mem.tagline else "",
                Span(state.replace("_", " ").upper(), cls=f"state-badge state-badge--{state}"),
                cls="profile-header-info",
            ),
            cls="profile-header",
        ),
        cls="profile-hero",
    )

    # Info sections
    details = Div(
        _info_section("About", [
            ("Website type", mem.website_type.replace("_", " ").title()),
            ("Primary goal", mem.primary_goal.replace("_", " ").title()),
            ("Description", mem.description or "Not provided"),
        ]),
        _info_section("Services", [
            ("Services", ", ".join(mem.services) if mem.services else "None listed"),
        ]),
        _info_section("Contact", [
            ("Email", mem.contact_email or "Not provided"),
            ("Phone", mem.contact_phone or "Not provided"),
            ("Address", mem.address or "Not provided"),
        ]),
        _info_section("Theme", [
            ("Theme", mem.theme.title()),
            ("Primary color", mem.primary_color),
            ("Secondary color", mem.secondary_color),
        ]),
        cls="profile-details",
    )

    content = Div(
        info_card,
        details,
        cls="project-page",
    )

    return page_layout(content, title=f"Okenaba - {mem.business_name}", project_id=pid, active_nav="profile")


def _info_section(title, items):
    """Render a labeled group of key-value pairs."""
    rows = []
    for label, value in items:
        rows.append(
            Div(
                Span(label, cls="info-label"),
                Span(value, cls="info-value"),
                cls="info-row",
            )
        )
    return Div(
        H2(title, cls="info-section-title"),
        Div(*rows, cls="info-rows"),
        cls="info-section",
    )
