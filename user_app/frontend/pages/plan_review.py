"""Plan review page (PLAN_READY state)."""

from fasthtml.common import Div, H1, H3, P, Form, Button, Section, A, Span

from user_app.frontend.layout import page_layout


def plan_review_page(user, project):
    """Show the AI-generated site plan for user approval."""
    pid = project.id
    plan = project.site_plan

    meta = Div(
        Div(
            Span("Page Title", cls="plan-meta-label"),
            Div(plan.page_title, cls="plan-meta-title"),
            cls="plan-meta-row",
        ),
        Div(
            Span("Meta Description", cls="plan-meta-label"),
            P(plan.meta_description, cls="plan-meta-desc"),
            cls="plan-meta-row",
        ),
        cls="plan-meta",
    )

    section_cards = []
    for i, s in enumerate(plan.sections, 1):
        section_cards.append(
            Div(
                Div(
                    Span(str(i), cls="plan-section-number"),
                    Div(
                        H3(s.title, cls="plan-section-title"),
                        Div(s.purpose, cls="plan-section-purpose"),
                        cls="plan-section-header",
                    ),
                    cls="plan-section-top",
                ),
                P(s.content_notes, cls="plan-section-notes"),
                cls="plan-section-card",
            ),
        )

    content = Section(
        Div(
            Div(
                Span(f"{len(plan.sections)} sections", cls="plan-count-badge"),
                cls="action-step-badge-wrap",
            ),
            H1("Your Site Plan", cls="step-title"),
            P(
                "Review the structure below. Each section maps to a part of your final page. "
                "Approve when you're ready to build.",
                cls="step-description",
            ),
            meta,
            Div(*section_cards, cls="plan-sections"),
            Div(
                A("Back to Projects", href="/", cls="button button-secondary"),
                Form(
                    Button("Approve & Continue", cls="button button-primary", type="submit"),
                    method="post", action=f"/projects/{pid}/approve",
                ),
                cls="button-group",
            ),
            cls="step-content",
        ),
        cls="step",
    )

    return page_layout(content, user=user, title="Okenaba - Review Plan", project_id=pid, active_nav="projects")
