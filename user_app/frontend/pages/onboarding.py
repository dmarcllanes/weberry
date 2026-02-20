"""Onboarding — Brain Dump form (3-step wizard)."""

from fasthtml.common import (
    Div, H1, H2, P, Form, Button, Input, Textarea, Label, Span,
    Section, Select, Option, A, Img, Small,
)

from user_app.frontend.layout import page_layout


def render_asset_card(asset, project_id):
    """Render a single uploaded asset card (used by onboarding and upload endpoint)."""
    return Div(
        Img(src=asset.url, alt=asset.label, cls="asset-card-img"),
        Div(
            Span(asset.label.capitalize(), cls="asset-card-label"),
            Span(f"{asset.width}x{asset.height} {asset.orientation}", cls="asset-card-dims"),
            cls="asset-card-info",
        ),
        Button("Remove", type="button", cls="btn btn-sm btn-ghost btn-delete",
               hx_delete=f"/pages/{project_id}/assets?url={asset.url}",
               hx_target="closest .asset-card", hx_swap="outerHTML"),
        cls="asset-card",
    )


def _step_indicator():
    """3-step indicator: Basics, Brand, Details."""
    labels = ["Basics", "Brand", "Details"]
    items = []
    for i, lbl in enumerate(labels):
        step_num = i + 1
        cls = "si-circle si-active" if step_num == 1 else "si-circle"
        items.append(
            Div(
                Div(str(step_num), cls=cls,
                    onclick=f"goToStep({step_num})" if step_num > 1 else None),
                Span(lbl, cls="si-label si-label-active" if step_num == 1 else "si-label"),
                cls="si-step",
            )
        )
        if step_num < len(labels):
            items.append(Div(cls="si-connector"))
    return Div(*items, cls="step-indicator", id="stepIndicator")


def onboarding_page(user, project):
    """3-step Brain Dump wizard — collects input then auto-generates."""
    pid = project.id
    mem = project.brand_memory
    bname = mem.business_name if mem else ""
    desc = mem.description if mem else ""
    goal = mem.primary_goal if mem else ""

    goals = [
        ("", "What's the #1 thing this site should do?"),
        ("collect_emails", "Collect Emails / Leads"),
        ("sell_preorder", "Sell a Pre-order"),
        ("schedule_call", "Schedule Calls / Demos"),
        ("build_authority", "Build Authority"),
        ("direct_traffic", "Direct Traffic to Another Link"),
    ]

    # --- Step 1: The Basics ---
    industry_val = mem.services[0] if mem and mem.services else ""

    step1 = Div(
        Div(
            H1("The Basics", cls="step-title"),
            P("Tell us about your business in 30 seconds.", cls="step-description"),
            Div(
                Div(
                    Label("Business name", _for="business_name", cls="label"),
                    Input(type="text", name="business_name", id="business_name",
                          value=bname, placeholder="e.g., Sarah's Photography",
                          cls="input", oninput="clearFieldError(this)"),
                    Span(cls="field-error", id="business_name_error", role="alert"),
                    cls="form-group",
                ),
                Div(
                    Label("Industry", _for="industry", cls="label"),
                    Input(type="text", name="industry", id="industry",
                          value=industry_val,
                          placeholder="e.g., Coffee Shop, SaaS, Photography",
                          cls="input", oninput="clearFieldError(this)"),
                    Span(cls="field-error", id="industry_error", role="alert"),
                    cls="form-group",
                ),
                Div(
                    Label("Describe what you do", Span("(optional)", cls="optional"),
                          _for="description", cls="label"),
                    Textarea(
                        desc,
                        name="description", id="description",
                        placeholder="Include your services, audience, what makes you different...",
                        cls="input input-textarea", rows="3",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Primary goal", _for="primary_goal", cls="label"),
                    Select(
                        *[Option(lbl, value=val, selected=(val == goal)) for val, lbl in goals],
                        name="primary_goal", id="primary_goal", cls="input",
                        onchange="clearFieldError(this)",
                    ),
                    Span(cls="field-error", id="primary_goal_error", role="alert"),
                    cls="form-group",
                ),
                Div(
                    Button("Next", type="button", cls="button button-primary",
                           onclick="nextStep(event)"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step1", cls="step step-active",
    )

    # --- Step 2: Brand Identity ---
    step2 = Div(
        Div(
            H1("Brand Identity", cls="step-title"),
            P("Set the personality and look of your site.", cls="step-description"),
            Div(
                Div(
                    Label("Tagline", Span("(optional)", cls="optional"),
                          _for="tagline", cls="label"),
                    Input(type="text", name="tagline", id="tagline",
                          value=mem.tagline if mem and mem.tagline else "",
                          placeholder="e.g., Your neighborhood coffee experts",
                          cls="input"),
                    cls="form-group",
                ),
                Div(
                    Label("Brand color", _for="primary_color", cls="label"),
                    Div(
                        *[Span(
                            cls="color-swatch",
                            style=f"background-color:{c}",
                            onclick=f"document.getElementById('primary_color').value='{c}'",
                          ) for c in [
                            "#4F46E5", "#2563EB", "#059669", "#D97706",
                            "#DC2626", "#7C3AED", "#0891B2", "#1F2937",
                        ]],
                        cls="color-swatch-row",
                    ),
                    Input(type="color", name="primary_color", id="primary_color",
                          value=mem.primary_color if mem and mem.primary_color else "#4F46E5",
                          cls="color-input"),
                    cls="form-group",
                ),
                Div(
                    Label("Tone / Vibe", _for="theme", cls="label"),
                    Select(
                        Option("Professional", value="professional",
                               selected=(mem and mem.theme == "professional")),
                        Option("Friendly & Casual", value="friendly",
                               selected=(mem and mem.theme == "friendly")),
                        Option("Bold & Energetic", value="bold",
                               selected=(mem and mem.theme == "bold")),
                        Option("Elegant & Minimal", value="elegant",
                               selected=(mem and mem.theme == "elegant")),
                        name="theme", id="theme", cls="input",
                    ),
                    cls="form-group",
                ),
                Div(
                    Button("Back", type="button", cls="button button-secondary",
                           onclick="prevStep()"),
                    Button("Next", type="button", cls="button button-primary",
                           onclick="nextStep(event)"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step2", cls="step",
    )

    # --- Step 3: Contact & Details ---
    step3 = Div(
        Div(
            H1("Contact & Details", cls="step-title"),
            P(
                "Add your contact info so visitors can reach you. "
                "All fields are optional — skip if you prefer.",
                cls="step-description",
            ),
            Div(
                Div(
                    Label("Contact email", Span("(optional)", cls="optional"),
                          _for="contact_email", cls="label"),
                    Input(type="email", name="contact_email", id="contact_email",
                          value=mem.contact_email if mem and mem.contact_email else "",
                          placeholder="hello@yourbusiness.com",
                          cls="input"),
                    cls="form-group",
                ),
                Div(
                    Label("Contact phone", Span("(optional)", cls="optional"),
                          _for="contact_phone", cls="label"),
                    Input(type="tel", name="contact_phone", id="contact_phone",
                          value=mem.contact_phone if mem and mem.contact_phone else "",
                          placeholder="+1 (555) 123-4567",
                          cls="input"),
                    cls="form-group",
                ),
                Div(
                    Label("Address / Location", Span("(optional)", cls="optional"),
                          _for="address", cls="label"),
                    Input(type="text", name="address", id="address",
                          value=mem.address if mem and mem.address else "",
                          placeholder="123 Main St, City, State",
                          cls="input"),
                    cls="form-group",
                ),
                Div(
                    Button("Back", type="button", cls="button button-secondary",
                           onclick="prevStep()"),
                    Button("Build My Site", type="submit", cls="button button-primary",
                           onclick="return validateAndSubmit()"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step3", cls="step",
    )

    form = Form(
        Div(id="onboarding-active", data_delete_url=f"/pages/{pid}/delete",
            style="display:none"),
        _step_indicator(),
        Div(step1, step2, step3, cls="wizard"),
        method="post", action=f"/pages/{pid}/braindump",
    )

    content = Div(form, cls="onboarding-layout")

    return page_layout(content, user=user, title="Okenaba - Brain Dump", project_id=pid, active_nav="pages")


def waiting_for_plan_page(user, project):
    """After memory is saved — prompt to generate site (template flow)."""
    pid = project.id
    name = project.brand_memory.business_name if project.brand_memory else "your site"

    content = Section(
        Div(
            Div(
                Div(cls="action-icon-inner"),
                cls="action-icon action-icon--plan",
            ),
            H1("Ready to Generate Your Site", cls="step-title"),
            P(
                f"We have everything we need about {name}. "
                "Our AI will pick the best template, write your copy, "
                "and build your site in seconds.",
                cls="step-description",
            ),
            Div(
                Div(
                    Span("AI picks the perfect template", cls="action-feature-text"),
                    cls="action-feature",
                ),
                Div(
                    Span("Custom copy tailored to your business", cls="action-feature-text"),
                    cls="action-feature",
                ),
                Div(
                    Span("Instant rendering, no waiting", cls="action-feature-text"),
                    cls="action-feature",
                ),
                cls="action-features",
            ),
            Div(
                A("Back to Pages", href="/pages", cls="button button-secondary"),
                Form(
                    Button("Generate My Site", cls="button button-primary", type="submit",
                           onclick="return showLoading('Generating your site...')"),
                    method="post", action=f"/pages/{pid}/plan",
                ),
                cls="button-group",
            ),
            cls="step-content action-page",
        ),
        cls="step",
    )

    return page_layout(content, user=user, title="Okenaba - Generate Site", project_id=pid, active_nav="pages")
