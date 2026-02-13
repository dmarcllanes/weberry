"""Preview page (SITE_GENERATED / PREVIEW states)."""

from fasthtml.common import Div, H1, P, Form, Button, Section, Iframe, A

from user_app.frontend.layout import page_layout


def preview_page(project):
    """Show generated site in iframe with publish button."""
    pid = project.id

    content = Div(
        Section(
            Div(
                H1("Preview Your Site", cls="step-title"),
                P(
                    "Here's how your website looks. When you're happy with it, "
                    "hit publish to go live!",
                    cls="step-description",
                ),
                Iframe(
                    src=f"/projects/{pid}/preview-render",
                    cls="site-preview-frame",
                    title="Site preview",
                ),
                Div(
                    Form(
                        Button("Publish My Site", cls="button button-primary", type="submit",
                               onclick="return showLoading('Publishing your site...')"),
                        method="post", action=f"/projects/{pid}/publish",
                    ),
                    A("Edit Content", href=f"/projects/{pid}/edit", cls="button button-secondary"),
                    A("Exit", href="/", cls="button button-secondary"),
                    cls="button-group",
                    style="margin-top:2rem",
                ),
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    return page_layout(content, title="Okenaba - Preview", project_id=pid, active_nav="projects")
