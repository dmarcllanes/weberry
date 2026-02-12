"""Site detail page — shows published website information and assets."""

from fasthtml.common import (
    Div, H1, H2, H3, P, Button, Section, Span, A, Iframe,
)

from user_app.frontend.layout import page_layout


def site_detail_page(project, public_url=None, trial_info=None):
    """Show the website details, preview, plan, and publishing info."""
    pid = project.id
    mem = project.brand_memory
    name = mem.business_name if mem else "Your Site"
    state = project.state.value

    # Status bar
    status = Div(
        Div(
            Span("Status", cls="info-label"),
            Span(state.replace("_", " ").upper(), cls=f"state-badge state-badge--{state}"),
            cls="status-row",
        ),
        cls="site-status-bar",
    )

    sections = [status]

    # Live URL section (only if published)
    if public_url:
        trial_banner = ""
        if trial_info and trial_info.get("days_remaining") is not None:
            days = trial_info["days_remaining"]
            trial_banner = Div(
                Span(f"Free trial: {days} day{'s' if days != 1 else ''} remaining",
                     cls="trial-banner-text"),
                cls="trial-banner",
            )

        url_section = Div(
            H2("Live URL", cls="info-section-title"),
            trial_banner,
            Div(
                Div(public_url, cls="link-display", id="siteLink"),
                Div(
                    A("Visit Site", href=f"/sites/{pid}", cls="button button-primary",
                      target="_blank", style="flex:1"),
                    Button("Copy Link", type="button", cls="button button-secondary",
                           onclick=f"copySiteLink('{public_url}')", style="flex:1"),
                    cls="button-group",
                ),
                cls="url-box",
            ),
            cls="info-section",
        )
        sections.append(url_section)

    # Site preview (if site has been generated)
    if project.site_version and project.site_version.html:
        preview_section = Div(
            H2("Preview", cls="info-section-title"),
            Iframe(
                src=f"/projects/{pid}/preview-render",
                cls="site-preview-frame",
                title="Site preview",
            ),
            cls="info-section",
        )
        sections.append(preview_section)

    # Site plan (if available)
    if project.site_plan:
        plan = project.site_plan
        plan_cards = []
        for s in plan.sections:
            plan_cards.append(
                Div(
                    H3(s.title, cls="plan-section-title"),
                    P(s.purpose, cls="plan-section-purpose"),
                    P(s.content_notes, cls="plan-section-notes"),
                    cls="plan-section-card",
                )
            )
        plan_section = Div(
            H2("Site Plan", cls="info-section-title"),
            Div(
                Div(plan.page_title, cls="plan-meta-title"),
                P(plan.meta_description, cls="plan-meta-desc"),
                cls="plan-meta",
            ),
            Div(*plan_cards, cls="plan-sections"),
            cls="info-section",
        )
        sections.append(plan_section)

    # Site version info
    if project.site_version:
        ver = project.site_version
        version_section = Div(
            H2("Version", cls="info-section-title"),
            Div(
                Div(
                    Span("Version", cls="info-label"),
                    Span(str(ver.version), cls="info-value"),
                    cls="info-row",
                ),
                Div(
                    Span("Published", cls="info-label"),
                    Span("Yes" if ver.is_published else "No", cls="info-value"),
                    cls="info-row",
                ),
                cls="info-rows",
            ),
            cls="info-section",
        )
        sections.append(version_section)

    content = Div(*sections, cls="project-page")

    return page_layout(content, title=f"Okenaba - {name} Site", project_id=pid, active_nav="site")
