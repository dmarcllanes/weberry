"""Generating page (PLAN_APPROVED state)."""

from fasthtml.common import Div, H1, P, Form, Button, Section, A, Span

from user_app.frontend.layout import page_layout


def generating_page(user, project):
    """Prompt user to trigger site generation."""
    pid = project.id

    content = Section(
        Div(
            Div(
                Div(cls="action-icon-inner"),
                cls="action-icon action-icon--generate",
            ),
            Div(
                Span("Step 2 of 2", cls="action-step-badge"),
                cls="action-step-badge-wrap",
            ),
            H1("Generate Your Website", cls="step-title"),
            P(
                "Your plan is approved. Our AI will now build your site "
                "with optimized HTML and CSS — fast, clean, and ready to publish.",
                cls="step-description",
            ),
            Div(
                Div(
                    Span("Static HTML5 — no dependencies", cls="action-feature-text"),
                    cls="action-feature",
                ),
                Div(
                    Span("100/100 PageSpeed score", cls="action-feature-text"),
                    cls="action-feature",
                ),
                Div(
                    Span("Mobile-responsive design", cls="action-feature-text"),
                    cls="action-feature",
                ),
                cls="action-features",
            ),
            Div(
                A("Back to Projects", href="/", cls="button button-secondary"),
                Form(
                    Button("Generate My Site", cls="button button-primary", type="submit",
                           onclick="return showLoading('Building your website...')"),
                    method="post", action=f"/projects/{pid}/generate",
                ),
                cls="button-group",
            ),
            cls="step-content action-page",
        ),
        cls="step",
    )

    return page_layout(content, user=user, title="Okenaba - Generate Site", project_id=pid, active_nav="projects")
