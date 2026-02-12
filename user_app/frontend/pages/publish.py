"""Published page (PUBLISHED state)."""

from fasthtml.common import Div, H1, P, Button, Section, Span, Ul, Li, A

from user_app.frontend.layout import page_layout


def published_page(project, public_url, trial_info=None):
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
                A("Back to Dashboard", href="/", cls="button button-secondary",
                  style="margin-top:1rem"),
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    return page_layout(content, title="Okenaba - Published!", project_id=pid, active_nav="overview")
