"""Plan review page (PLAN_READY state)."""

from fasthtml.common import Div, H1, H3, P, Form, Button, Section, A

from user_app.frontend.layout import page_layout


def plan_review_page(project):
    """Show the AI-generated site plan for user approval."""
    pid = project.id
    plan = project.site_plan

    meta = Div(
        Div(plan.page_title, cls="plan-meta-title"),
        P(plan.meta_description, cls="plan-meta-desc"),
        cls="plan-meta",
    )

    section_cards = []
    for s in plan.sections:
        section_cards.append(
            Div(
                H3(s.title, cls="plan-section-title"),
                P(s.purpose, cls="plan-section-purpose"),
                P(s.content_notes, cls="plan-section-notes"),
                cls="plan-section-card",
            ),
        )

    content = Section(
        Div(
            H1("Your Site Plan", cls="step-title"),
            P(
                "Here's what we've planned for your website. "
                "Review the sections below and approve when you're ready.",
                cls="step-description",
            ),
            meta,
            Div(*section_cards, cls="plan-sections"),
            Div(
                Form(
                    Button("Approve & Continue", cls="button button-primary", type="submit"),
                    method="post", action=f"/projects/{pid}/approve",
                ),
                A("Exit", href="/", cls="button button-secondary"),
                cls="button-group",
            ),
            cls="step-content",
        ),
        cls="step",
    )

    return page_layout(content, title="Okenaba - Review Plan", project_id=pid, active_nav="projects")
