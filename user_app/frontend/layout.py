"""Shared page layout components."""

from fasthtml.common import *

# --- SVG icon helpers (used in sidebar) ---

def _icon(path_data, size=18):
    return Safe(f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{path_data}</svg>')

_ICON_PAGES   = '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
_ICON_HELP    = '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>'
_ICON_BILLING = '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>'
_ICON_PROFILE = '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'
_ICON_THEME   = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
_ICON_LOGOUT  = '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/>'
_ICON_MENU    = '<line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>'


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

    header = Header(
        Div(
            Div(
                A(
                    Img(src="/static/img/favicon.svg", alt="", cls="logo-icon"),
                    Span("kenaba", cls="logo-wordmark"),
                    href="/", cls="logo",
                ),
                mobile_toggle,
                cls="header-top"
            ),
            Nav(
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
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Meta(name="theme-color", content="#2563eb"),
            Meta(name="mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
            Meta(name="apple-mobile-web-app-title", content="Okenaba"),
            Title(title),
            Link(rel='icon', type='image/svg+xml', href='/static/img/favicon.svg'),
            Link(rel="apple-touch-icon", href="/static/img/favicon.svg"),
            Link(rel="manifest", href="/static/manifest.json"),
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


def sidebar_layout(content, user=None, title="Okenaba", active_nav=None, analytics=None):
    """Left-sidebar layout for authenticated app pages (dashboard, profile, etc.)."""

    # Nav items: (label, href, key, icon_svg_paths)
    nav_items = [
        ("Pages",   "/pages",   "pages",   _ICON_PAGES),
        ("Help",    "/help",    "help",    _ICON_HELP),
    ]

    nav_links = []
    for label, href, key, paths in nav_items:
        cls = "sidebar-link active" if key == active_nav else "sidebar-link"
        nav_links.append(A(_icon(paths), label, href=href, cls=cls))

    # Stats section
    stats_section = ""
    if analytics:
        stats_section = Div(
            P("Overview", cls="sidebar-stats-title"),
            Div(
                Span("Total", cls="sidebar-stat-label"),
                Span(str(analytics.get("total", 0)), cls="sidebar-stat-value"),
                cls="sidebar-stat-row",
            ),
            Div(
                Span("Published", cls="sidebar-stat-label"),
                Span(str(analytics.get("published", 0)), cls="sidebar-stat-value"),
                cls="sidebar-stat-row",
            ),
            Div(
                Span("In Progress", cls="sidebar-stat-label"),
                Span(str(analytics.get("unfinished", 0)), cls="sidebar-stat-value"),
                cls="sidebar-stat-row",
            ),
            cls="sidebar-stats",
        )

    # Footer: user info, extra links, logout
    footer_items = []

    footer_items.append(
        A(_icon(_ICON_BILLING), "Billing", href="/billing",
          cls=f"sidebar-btn {'active' if active_nav == 'billing' else ''}"),
    )

    footer_items.append(
        A(_icon(_ICON_PROFILE), "Profile", href="/profile",
          cls=f"sidebar-btn {'active' if active_nav == 'profile' else ''}"),
    )

    if user:
        # User row: avatar + email
        if user.avatar_url:
            avatar = Div(Img(src=user.avatar_url, alt="Avatar"), cls="sidebar-avatar")
        else:
            avatar = Div(user.email[0].upper(), cls="sidebar-avatar")

        footer_items.insert(
            0,
            Div(avatar, Span(user.email, cls="sidebar-user-email"), cls="sidebar-user-row"),
        )

        footer_items.append(
            Form(
                Button(
                    _icon(_ICON_LOGOUT), "Logout",
                    type="submit",
                    cls="sidebar-btn sidebar-btn-danger",
                ),
                action="/logout", method="post",
            )
        )

    # Mobile overlay + toggle
    overlay = Div(
        cls="sidebar-overlay",
        id="sidebar-overlay",
        onclick="toggleSidebar()",
    )
    mobile_toggle = Button(
        _icon(_ICON_MENU, size=20),
        cls="sidebar-mobile-toggle",
        onclick="toggleSidebar()",
        aria_label="Open navigation",
    )

    sidebar = Aside(
        Div(
            A(
                Img(src="/static/img/favicon.svg", alt="", cls="logo-icon"),
                Span("kenaba", cls="logo-wordmark"),
                href="/", cls="sidebar-logo",
            ),
            cls="sidebar-logo-area",
        ),
        Nav(*nav_links, cls="sidebar-nav"),
        Div(cls="sidebar-spacer"),
        stats_section,
        Div(*footer_items, cls="sidebar-footer"),
        cls="sidebar",
        id="app-sidebar",
    )

    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Meta(name="theme-color", content="#2563eb"),
            Meta(name="mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
            Meta(name="apple-mobile-web-app-title", content="Okenaba"),
            Title(title),
            Link(rel="icon", type="image/svg+xml", href="/static/img/favicon.svg"),
            Link(rel="apple-touch-icon", href="/static/img/favicon.svg"),
            Link(rel="manifest", href="/static/manifest.json"),
            Link(rel="stylesheet", href="/static/app.css"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
                 rel="stylesheet"),
            Script(src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.7/dist/htmx.js"),
            Script(src="/static/app.js", defer=True),
        ),
        Body(
            overlay,
            mobile_toggle,
            Div(sidebar, Main(content, cls="sidebar-main"), cls="sidebar-layout"),
        ),
    )
