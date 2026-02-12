"""Preview page (SITE_GENERATED / PREVIEW states)."""

from fasthtml.common import Div, H1, P, Form, Button, Section, Iframe

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
                Form(
                    Button("Publish My Site", cls="button button-primary", type="submit",
                           style="margin-top:2rem"),
                    method="post", action=f"/projects/{pid}/publish",
                ),
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    return page_layout(content, title="Okenaba - Preview", project_id=pid, active_nav="overview")
