"""Published page (PUBLISHED state)."""

from fasthtml.common import Div, H1, P, Button, Section, Span, Ul, Li, A, H3

from user_app.frontend.layout import page_layout




def published_page(user, project, public_url, trial_info=None):
    """Success screen after publishing."""
    pid = project.id
    name = project.brand_memory.business_name if project.brand_memory else "Your site"

    trial_banner = None
    if trial_info and trial_info.get("days_remaining") is not None:
        days = trial_info["days_remaining"]
        trial_banner = Div(
            Span(f"Free trial: {days} day{'s' if days != 1 else ''} remaining", cls="trial-banner-text"),
            cls="trial-banner",
        )

    content = Div(
        Section(
            Div(
                A("← Back to Pages", href="/pages", cls="button button-secondary",
                  style="margin-bottom:1.5rem;display:inline-flex;align-items:center;gap:0.4rem;"),
                Div("\U0001f389", cls="success-icon"),
                H1("You're Live!", cls="step-title"),
                P(
                    f"{name} is now published and live on the web. "
                    "Share your link with the world!",
                    cls="step-description",
                ),
                trial_banner if trial_banner else "",
                Div(
                    P("Your site:", cls="link-label"),
                    Div(public_url, cls="link-display", id="siteLink"),
                    Button("Copy Link", type="button", cls="button button-secondary",
                           onclick=f"copySiteLink('{public_url}')"),
                    cls="success-link",
                ),
                Div(
                    P("Next steps:", cls="next-steps-title"),
                    Ul(
                        Li("Share your link on social media"),
                        Li("Add your link to your email signature"),
                        Li("Come back anytime to update your info"),
                        cls="next-steps-list",
                    ),
                    cls="next-steps",
                ),
                Div(
                    # Edit card
                    Div(
                        Div("✏️", cls="preview-action-icon"),
                        H3("Edit Content", cls="preview-action-title"),
                        P(
                            "Update copy or manually edit HTML — changes go live immediately.",
                            cls="preview-action-desc",
                        ),
                        A("Edit Content →", href=f"/pages/{pid}/edit",
                          cls="button button-secondary"),
                        cls="preview-action-card",
                    ),
                    # HTML editor shortcut
                    Div(
                        Div("🛠️", cls="preview-action-icon"),
                        H3("HTML Editor", cls="preview-action-title"),
                        P(
                            "Go hands-on and manually insert or rewrite any part of the page.",
                            cls="preview-action-desc",
                        ),
                        A("Open HTML Editor →", href=f"/pages/{pid}/edit?tab=html",
                          cls="button button-primary"),
                        cls="preview-action-card preview-action-card--deploy",
                    ),
                    cls="preview-actions",
                    style="margin-top:1.5rem",
                ),
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    return page_layout(content, user=user, title="Okenaba - Published!", project_id=pid, active_nav="pages")
