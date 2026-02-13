"""Shared page layout components."""

from fasthtml.common import (
    Html, Head, Body, Title, Meta, Link, Script,
    Div, Header, Footer, Main, Nav, A, Span, H1, P,
)


def page_layout(*content, title="Okenaba", step_indicator=None, project_id=None, active_nav=None, hide_nav=False):
    """Wrap page content in the shared header + footer shell."""
    nav_links = []
    if not hide_nav:
        for label, href, key in [
            ("Projects", "/", "projects"),
            ("Profile", "/profile", "profile"),
            ("Help", "#", "help"),
        ]:
            cls = "nav-link active" if key == active_nav else "nav-link"
            nav_links.append(A(label, href=href, cls=cls))

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
    """Numbered circle step indicator with connectors."""
    labels = ["Welcome", "About", "Story", "Contact"]
    items = []
    for i in range(1, total + 1):
        circle_cls = "si-circle"
        if i < current:
            circle_cls += " si-completed"
        elif i == current:
            circle_cls += " si-active"

        # Completed circles are clickable
        circle_attrs = {}
        if i < current:
            circle_attrs["onclick"] = f"goToStep({i})"
            circle_attrs["tabindex"] = "0"
            circle_attrs["role"] = "button"
            circle_attrs["aria_label"] = f"Go back to step {i}: {labels[i-1]}"

        label_cls = "si-label"
        if i <= current:
            label_cls += " si-label-active"

        step_item = Div(
            Div(str(i), cls=circle_cls, **circle_attrs),
            Span(labels[i - 1], cls=label_cls),
            cls="si-step",
        )
        items.append(step_item)

        # Add connector between circles (not after last)
        if i < total:
            conn_cls = "si-connector"
            if i < current:
                conn_cls += " si-connector-done"
            items.append(Div(cls=conn_cls))

    return Div(*items, cls="step-indicator", id="stepIndicator")


def error_banner(message):
    """Inline error banner."""
    return Div(message, cls="error-banner")
