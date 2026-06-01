"""Preview page (SITE_GENERATED / PREVIEW states)."""

from pathlib import Path

from fasthtml.common import (
    Div, H1, H2, H3, P, Form, Button, Section, Iframe, A, Span,
    Input, Details, Summary, Img, Label, Select, Option, Safe,
)

from user_app.frontend.layout import page_layout


def preview_page(user, project):
    """Show generated site in iframe with publish button and image editor."""
    pid = project.id

    browser_bar = Div(
        Div(
            Span(cls="browser-dot browser-dot--red"),
            Span(cls="browser-dot browser-dot--yellow"),
            Span(cls="browser-dot browser-dot--green"),
            cls="browser-dots",
        ),
        Div(
            Span("yoursite.okenaba.com", cls="browser-url-text"),
            cls="browser-url-bar",
        ),
        cls="browser-bar",
    )


    action_cards = Div(
        # Edit card
        Div(
            Div("✏️", cls="preview-action-icon"),
            H3("Edit Your Content", cls="preview-action-title"),
            P(
                "Fine-tune copy, swap images, or go hands-on with the raw HTML editor.",
                cls="preview-action-desc",
            ),
            A("Edit Content →", href=f"/pages/{pid}/edit", cls="button button-secondary"),
            cls="preview-action-card",
        ),
        # Deploy card
        Div(
            Div("🚀", cls="preview-action-icon"),
            H3("Deploy Your Site", cls="preview-action-title"),
            P(
                "Make it live in one click. You can keep editing even after deployment.",
                cls="preview-action-desc",
            ),
            Form(
                Button("Deploy Now →", cls="button button-primary", type="submit",
                       onclick="return showLoading('Deploying your site...')"),
                method="post", action=f"/pages/{pid}/publish",
            ),
            cls="preview-action-card preview-action-card--deploy",
        ),
        cls="preview-actions",
    )

    content = Section(
        Div(
            A(
                Safe("← Back to Pages"),
                href="/pages",
                cls="preview-back-link",
            ),
            H1("Preview Your Site", cls="step-title"),
            P(
                "Here's your generated website. Review it, then edit or deploy below.",
                cls="step-description",
            ),
            Div(
                browser_bar,
                Iframe(
                    src=f"/pages/{pid}/preview-render",
                    cls="site-preview-frame",
                    title="Site preview",
                ),
                cls="browser-chrome",
            ),
            action_cards,
            cls="step-content",
        ),
        cls="step preview-page-step",
    )

    return page_layout(content, user=user, title="Okenaba - Preview", project_id=pid, active_nav="pages")
