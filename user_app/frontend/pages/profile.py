"""Profile page — shows and allows editing of brand memory info."""

from fasthtml.common import (
    Div, H1, H2, P, Form, Button, Input, Textarea, Label, Span,
    Section, A, Select, Option, Img,
)

from user_app.frontend.layout import page_layout


def user_profile_page(user):
    """Display user account info only."""
    
    # User Info Section
    user_info = Section(
        H1("Account Settings", cls="step-title"),
        Div(
            Div(
                 Img(src=user.avatar_url, cls="profile-page-avatar", alt=user.full_name or "User") if user.avatar_url else Div(user.email[0].upper(), cls="profile-page-avatar-placeholder"),
                 Div(
                     H2(user.full_name or "User", cls="profile-page-name"),
                     P("Google Account", cls="profile-provider-badge"),
                     cls="profile-identity"
                 ),
                 cls="profile-header-b"
            ),
            Div(
                _info_row("Email", user.email),
                _info_row("User ID", user.id),
                _info_row("Credits", str(user.available_credits)),
                cls="info-rows"
            ),
            cls="profile-card"
        ),
        cls="step"
    )

    content = Div(
        user_info,
        cls="dashboard-content"
    )

    return page_layout(
        content,
        user=user,
        title="Okenaba - Account",
        active_nav="profile"
    )


def brand_profile_page(project):
    """Display the project's brand memory information."""
    pid = project.id
    mem = project.brand_memory
    state = project.state.value

    if not mem:
        content = Section(
            Div(
                H1("Brand Profile", cls="step-title"),
                P("No profile information yet. Complete the onboarding first.",
                  cls="step-description"),
                A("Go to Setup", href=f"/pages/{pid}", cls="button button-primary",
                  style="max-width:300px;display:inline-block"),
                cls="step-content",
            ),
            cls="step",
        )
        return page_layout(content, title="Brand Profile", project_id=pid, active_nav="profile")

    # Display card
    return page_layout(brand_info_component(project), title=f"{mem.business_name} - Profile", project_id=pid, active_nav="profile")


def brand_info_component(project):
    """Reusable component to display brand memory details."""
    pid = project.id
    mem = project.brand_memory
    state = project.state.value
    
    if not mem:
        return Div(P("No brand info available."))

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
        _info_section("Timestamps", [
            ("Created", project.created_at.strftime("%b %d, %Y at %I:%M %p") if project.created_at else "Unknown"),
            ("Last Updated", project.updated_at.strftime("%b %d, %Y at %I:%M %p") if project.updated_at else "Unknown"),
        ]),
        _info_section("Theme", [
            ("Theme", mem.theme.title()),
            ("Primary color", mem.primary_color),
            ("Secondary color", mem.secondary_color),
        ]),
        cls="profile-details",
    )

    return Div(
        info_card,
        details,
        cls="project-page",  # Reusing project-page class for spacing
    )


def _info_section(title, items):
    """Render a labeled group of key-value pairs."""
    rows = []
    for label, value in items:
        rows.append(_info_row(label, value))
    return Div(
        H2(title, cls="info-section-title"),
        Div(*rows, cls="info-rows"),
        cls="info-section",
    )

def _info_row(label, value):
    return Div(
        Span(label, cls="info-label"),
        Span(value, cls="info-value"),
        cls="info-row",
    )
