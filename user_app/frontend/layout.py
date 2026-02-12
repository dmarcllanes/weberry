"""Shared page layout components."""

from fasthtml.common import (
    Html, Head, Body, Title, Meta, Link, Script,
    Div, Header, Footer, Main, Nav, A, Span, H1, P,
)


def page_layout(*content, title="Okenaba", step_indicator=None, project_id=None, active_nav=None):
    """Wrap page content in the shared header + footer shell."""
    nav_links = [A("Home", href="/landing", cls="nav-link active" if active_nav == "home" else "nav-link")]
    if project_id:
        for label, href, key in [
            ("Overview", f"/projects/{project_id}", "overview"),
            ("Profile", f"/projects/{project_id}/profile", "profile"),
            ("My Site", f"/projects/{project_id}/site", "site"),
        ]:
            cls = "nav-link active" if key == active_nav else "nav-link"
            nav_links.append(A(label, href=href, cls=cls))
    nav_links.append(A("Help", href="#", cls="nav-link"))

    header = Header(
        Div(
            A(
                Span("O", cls="logo-icon"),
                Span("kenaba", cls="logo-text"),
                href="/", cls="logo",
            ),
            Nav(
                *nav_links,
                cls="nav",
            ),
            cls="header-content",
        ),
        cls="header",
    )

    main_children = []
    if step_indicator is not None:
        main_children.append(step_indicator)
    main_children.extend(content)

    main = Main(*main_children, cls="main")

    footer = Footer(
        Div(
            A("Help & Support", href="#", cls="footer-link"),
            Span("\u2022", cls="footer-divider"),
            A("Privacy Policy", href="#", cls="footer-link"),
            Span("\u2022", cls="footer-divider"),
            A("Terms", href="#", cls="footer-link"),
            cls="footer-content",
        ),
        cls="footer",
    )

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title(title),
            Link(rel="stylesheet", href="/static/app.css"),
            Script(src="/static/app.js", defer=True),
        ),
        Body(
            Div(header, main, cls="app"),
            footer,
        ),
    )


def make_step_indicator(current, total):
    """Progress bar with step label."""
    pct = int((current / total) * 100)
    return Div(
        Span(f"Step {current} of {total}", cls="step-label", id="stepLabel"),
        Div(
            Div(cls="progress-fill", id="progressFill", style=f"width:{pct}%"),
            cls="progress-bar",
        ),
        cls="step-indicator",
    )


def error_banner(message):
    """Inline error banner."""
    return Div(message, cls="error-banner")
