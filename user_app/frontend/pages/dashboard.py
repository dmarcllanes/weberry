"""Dashboard page — project list or welcome screen."""

from fasthtml.common import Div, H1, H3, P, A, Span, Form, Button, Section, Safe

from user_app.frontend.layout import page_layout

_FRIENDLY_STATE = {
    "draft": "Setting up",
    "input_ready": "Setting up",
    "memory_ready": "Ready to plan",
    "plan_ready": "Plan ready",
    "plan_approved": "Ready to build",
    "site_generated": "Ready to publish",
    "preview": "Ready to publish",
    "published": "Live",
    "error": "Needs attention",
}


def dashboard_page(user, projects, show_new_button=True, active_tab="unfinished", page=1):
    """Show welcome CTA if no projects, otherwise project cards with tabs and pagination."""
    
    # Analytics Data (calculated on full list)
    total_projects = len(projects)
    published_projects_list = [p for p in projects if p.state.value == "published"]
    published_count = len(published_projects_list)
    unfinished_count = total_projects - published_count

    # Filter based on tab
    if active_tab == "live":
        display_projects = published_projects_list
    elif active_tab == "unfinished":
        display_projects = [p for p in projects if p.state.value != "published"]
    else:  # all
        display_projects = projects
    
    # Pagination Logic
    ITEMS_PER_PAGE = 4
    total_items = len(display_projects)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paginated_projects = display_projects[start_idx:end_idx]

    # Tabs UI
    tabs = Div(
        A("All", href="?tab=all&page=1", 
            cls=f"tab-link {'active' if active_tab == 'all' else ''}"),
        A("Live", href="?tab=live&page=1", 
            cls=f"tab-link {'active' if active_tab == 'live' else ''}"),
        A("Unfinished", href="?tab=unfinished&page=1", 
            cls=f"tab-link {'active' if active_tab == 'unfinished' else ''}"),
        cls="dashboard-tabs",
        style="display:flex;gap:1.5rem;margin-bottom:1.5rem;border-bottom:1px solid var(--color-border)"
    )

    cards = []
    if not projects:
        # First-time user empty state
        cards.append(Div(
            Div("\u2728", style="font-size: 2rem; margin-bottom: 0.5rem"),
            H3("Ready to build your first website?", style="margin-bottom: 0.5rem; color:var(--color-text)"),
            P("Create your online presence in minutes. No technical skills needed.", 
              style="color:var(--color-text-light); margin-bottom: 1rem"),
            style="grid-column:1/-1;text-align:center;padding:3rem;background:var(--color-background-alt);border-radius:var(--radius-md);border:1px dashed var(--color-border);display:flex;flex-direction:column;align-items:center;"
        ))
    elif not paginated_projects:
        # Filter empty state
        cards.append(Div(P("No pages in this category.", style="color:var(--color-text-light);font-style:italic"), style="grid-column:1/-1;text-align:center;padding:2rem"))
    else:
        for p in paginated_projects:
            name = p.brand_memory.business_name if p.brand_memory else "Untitled"
            state = p.state.value
            friendly = _FRIENDLY_STATE.get(state, state.replace("_", " "))
            cards.append(
                Div(
                    A(
                        Div(name, cls="project-card-name"),
                        Span(friendly, cls=f"state-badge state-badge--{state}"),
                        href=f"/pages/{p.id}",
                        cls="project-card-link",
                    ),
                    Div(
                        Div(
                            A("View", cls="btn btn-outline btn-sm", href=f"/pages/{p.id}"),
                            A("Edit", cls="btn btn-outline btn-sm", href=f"/pages/{p.id}/edit"),
                            Button("Details", 
                                    cls="btn btn-outline btn-sm",
                                    hx_get=f"/pages/{p.id}/details",
                                    hx_target="#modal-body",
                                    onclick="document.getElementById('project-modal').style.display = 'flex'"),
                            cls="project-card-buttons"
                        ),
                        Form(
                            Button("Delete", cls="btn btn-ghost btn-sm btn-delete", type="submit",
                                onclick="return confirm('Delete this page? This cannot be undone.')"),
                            method="post", action=f"/pages/{p.id}/delete",
                        ),
                        cls="project-card-actions"
                    ),
                    cls="project-card",
                ),
            )

    # Pagination UI
    pagination = ""
    if total_pages > 1:
        prev_btn = A("\u2190 Prev", href=f"?tab={active_tab}&page={page-1}", cls="btn btn-outline btn-sm") if page > 1 else Button("\u2190 Prev", cls="btn btn-outline btn-sm", disabled=True)
        next_btn = A("Next \u2192", href=f"?tab={active_tab}&page={page+1}", cls="btn btn-outline btn-sm") if page < total_pages else Button("Next \u2192", cls="btn btn-outline btn-sm", disabled=True)
        
        pagination = Div(
            prev_btn,
            Span(f"Page {page} of {total_pages}", style="font-size:0.9rem;color:var(--color-text-light)"),
            next_btn,
            style="display:flex;justify-content:center;align-items:center;gap:1rem;margin-top:2rem"
        )

    children = [
        H1("Your Pages", cls="step-title"),
        tabs,
        Div(*cards, cls="project-grid"),
        pagination if pagination else "",
    ]
    
    available = user.available_credits
    if show_new_button:
        credit_label = (
            f"{available} credit{'s' if available != 1 else ''} remaining"
        )
        credit_color = "var(--color-success)" if available > 1 else "var(--color-warning)"
        children.append(
            Div(
                Form(
                    Button("+ New Page", cls="button button-primary", type="submit",
                            style="max-width:300px"),
                    method="post", action="/pages",
                ),
                P(credit_label,
                  style=f"margin-top:0.5rem;font-size:0.8rem;color:{credit_color};font-weight:500"),
                style="display:flex;flex-direction:column;align-items:center;margin-top:2rem"
            )
        )
    else:
        children.append(
            Div(
                Button("+ New Page", cls="button button-primary", disabled=True,
                        style="max-width:300px;opacity:0.5;cursor:not-allowed"),
                P(
                    "No credits left. ",
                    A("Buy credits →", href="/billing",
                      style="color:var(--color-primary);font-weight:600;text-decoration:none"),
                    style="margin-top:0.5rem;font-size:0.85rem;color:var(--color-text-light)"
                ),
                style="display:flex;flex-direction:column;align-items:center;margin-top:2rem"
            )
        )
    
    # Modal for project details
    modal = Div(
        Div(
            Div(
                Div(
                    Div("Page Details", style="font-weight:700;font-size:1.25rem"),
                    Button("\u2715", onclick="document.getElementById('project-modal').style.display = 'none'",
                            cls="modal-close"),
                    style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;border-bottom:1px solid var(--color-border);padding-bottom:1rem"
                ),
                Div(id="modal-body", cls="modal-body-content"),
                cls="modal-content",
            ),
            cls="modal-overlay",
            onclick="if(event.target == this) this.parentElement.style.display = 'none'"
        ),
        id="project-modal",
        style="display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background: rgba(0,0,0,0.5); justify-content:center; align-items:center;"
    )

    # Analytics Footer (Hidden by default, shown via fixed position)
    # Icons (Simple SVGs)
    icon_project = P(Safe("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>"""), cls="analytics-icon")
    icon_published = P(Safe("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1 4-10 15.3 15.3 0 0 1 4-10z"></path></svg>"""), cls="analytics-icon")
    icon_progress = P(Safe("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>"""), cls="analytics-icon")

    analytics_footer = Div(
        Div(
            Div(icon_project, Span("Total Pages:", cls="analytics-label"), Span(str(total_projects), cls="analytics-value"), cls="analytics-item"),
            Div(cls="analytics-divider"),
            Div(icon_published, Span("Published:", cls="analytics-label"), Span(str(published_count), cls="analytics-value"), cls="analytics-item"),
            Div(cls="analytics-divider"),
            Div(icon_progress, Span("In Progress:", cls="analytics-label"), Span(str(unfinished_count), cls="analytics-value"), cls="analytics-item"),
            cls="analytics-content"
        ),
        cls="analytics-footer"
    )

    content = Div(
        Div(*children, cls="step-content"),
        modal,
        analytics_footer,
        cls="dashboard-content",
    )

    return page_layout(content, user=user, title="Okenaba - Pages", active_nav="pages", hide_footer=True)
