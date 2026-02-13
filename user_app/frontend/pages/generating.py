"""Generating page (PLAN_APPROVED state)."""

from fasthtml.common import Div, H1, P, Form, Button, Section, A

from user_app.frontend.layout import page_layout


def generating_page(project):
    """Prompt user to trigger site generation."""
    pid = project.id

    content = Section(
        Div(
            Div("\U0001f680", cls="step-icon"),
            H1("Generate Your Website", cls="step-title"),
            P(
                "Your plan is approved! Click below to generate "
                "your website. This may take a moment.",
                cls="step-description",
            ),
            Div(
                Form(
                    Button("Generate My Site", cls="button button-primary", type="submit",
                           onclick="return showLoading('Building your website...')"),
                    method="post", action=f"/projects/{pid}/generate",
                ),
                A("Exit", href="/", cls="button button-secondary"),
                cls="button-group",
            ),
            cls="step-content action-page",
        ),
        cls="step",
    )

    return page_layout(content, title="Okenaba - Generate Site", project_id=pid, active_nav="projects")
