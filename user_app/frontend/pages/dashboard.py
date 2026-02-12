"""Dashboard page — project list or welcome screen."""

from fasthtml.common import Div, H1, P, A, Span, Form, Button, Section

from user_app.frontend.layout import page_layout

_FRIENDLY_STATE = {
    "draft": "Setting up",
    "input_ready": "Setting up",
    "memory_ready": "Ready to plan",
    "plan_ready": "Plan ready",
    "plan_approved": "Ready to build",
    "site_generated": "Ready to publish",
    "preview": "Ready to publish",
    "published": "Live",
    "error": "Needs attention",
}


def dashboard_page(user, projects):
    """Show welcome CTA if no projects, otherwise project cards."""
    if not projects:
        content = Section(
            Div(
                Div("\u2728", cls="step-icon"),
                H1("Welcome to Okenaba", cls="step-title"),
                P(
                    "Create your online presence in minutes. "
                    "No technical skills needed.",
                    cls="step-description",
                ),
                Form(
                    Button("Create My Website", cls="button button-primary", type="submit"),
                    method="post", action="/projects",
                ),
                cls="step-content dashboard-welcome",
            ),
            cls="step",
        )
    else:
        cards = []
        for p in projects:
            name = p.brand_memory.business_name if p.brand_memory else "Untitled"
            state = p.state.value
            friendly = _FRIENDLY_STATE.get(state, state.replace("_", " "))
            cards.append(
                A(
                    Div(name, cls="project-card-name"),
                    Span(friendly, cls=f"state-badge state-badge--{state}"),
                    href=f"/projects/{p.id}",
                    cls="project-card",
                ),
            )
        content = Div(
            Div(
                H1("Your Projects", cls="step-title"),
                Div(*cards, cls="project-grid"),
                Form(
                    Button("New Project", cls="button button-primary", type="submit",
                           style="margin-top:2rem;max-width:300px"),
                    method="post", action="/projects",
                ),
                cls="step-content",
            ),
            cls="dashboard-content",
        )

    return page_layout(content, title="Okenaba - Dashboard")
