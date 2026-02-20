"""Shared page layout components."""

from fasthtml.common import *


def page_layout(content, user=None, title="Okenaba", step_indicator=None, project_id=None, active_nav=None, hide_nav=False, hide_footer=False):
    """Wrap page content in the shared header + footer shell."""
    nav_links = []
    if not hide_nav:
        items = [
            ("Pages", "/pages", "pages"),
            ("Help", "/help", "help"),
        ]
        
        for i, (label, href, key) in enumerate(items):
            cls = "nav-link active" if key == active_nav else "nav-link"
            nav_links.append(A(label, href=href, cls=cls))
            # Add divider if not the last item
            if i < len(items) - 1:
                 nav_links.append(Span(cls="nav-item-divider"))
        
        # User Menu / Profile
        if user:
            # Add divider between last link and user menu
            if items:
                nav_links.append(Span(cls="nav-item-divider"))

            avatar_content = Span(user.email[0].upper(), cls="avatar-initial")
            if user.avatar_url:
                avatar_content = Img(src=user.avatar_url, cls="avatar-img", alt="Profile")
            
            user_menu = Div(
                Button(
                    avatar_content,
                    # Small dropdown arrow
                    Span("▼", cls="dropdown-caret"),
                    cls="user-avatar-btn",
                    onclick="toggleUserMenu()",
                    aria_label="User menu",
                    title="User menu"
                ),
                Div(
                    Div(user.email, cls="dropdown-header"),
                    A("Billing", href="/billing", cls="dropdown-item"),
                    A("Profile", href="/profile", cls="dropdown-item"),
                    Form(
                        Button("Logout", type="submit", cls="dropdown-item"),
                        action="/logout", method="post",
                    ),
                    id="user-dropdown",
                    cls="dropdown-menu"
                ),
                cls="user-menu-container"
            )
            nav_links.append(user_menu)
        else:
             if items:
                 nav_links.append(Span(cls="nav-item-divider"))
             nav_links.append(A("Login", href="/login", cls="nav-link"))

    # Mobile toggle button
    mobile_toggle = Button(
        Span(cls="hamburger-icon"),
        cls="mobile-toggle",
        onclick="toggleMobileMenu()",
        aria_label="Toggle navigation"
    )

    # Theme toggle button
    theme_toggle = Button(
        "☀️", # Default icon, JS will update
        cls="theme-toggle",
        onclick="toggleTheme()",
        aria_label="Toggle theme",
        title="Toggle dark/light mode"
    )

    header = Header(
        Div(
            Div(
                A(
                    "Okenaba",
                    href="/", cls="logo",
                ),
                Div(
                    mobile_toggle,
                    style="display:flex;gap:0.5rem;align-items:center"
                ),
                cls="header-top"
            ),
            Nav(
                theme_toggle,
                Span(cls="nav-item-divider"),
                *nav_links,
                cls="nav",
                id="main-nav"
            ),
            cls="header-content",
        ),
        cls="header",
    )

    main_children = []
    if step_indicator is not None:
        main_children.append(step_indicator)
    if isinstance(content, (list, tuple)):
        main_children.extend(content)
    else:
        main_children.append(content)

    main = Main(*main_children, cls="main")

    footer = None
    if not hide_footer:
        footer = Footer(
            Div(
                A("Help & Support", href="/help", cls="footer-link"),
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
            Link(rel='icon', type='image/svg+xml', href='/static/img/favicon.svg'),
            Link(rel="stylesheet", href="/static/app.css"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap", rel="stylesheet"),
            Script(src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.7/dist/htmx.js"),
            Script(src="/static/app.js", defer=True),
        ),
        Body(
            Div(header, main, cls="app"),
            footer if footer else "",
        ),
    )


def make_step_indicator(current, total):
    """Numbered circle step indicator with connectors."""
    labels = ["Welcome", "About", "Story", "Assets", "Contact"]
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
