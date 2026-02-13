"""Onboarding wizard (DRAFT / INPUT_READY states)."""

from fasthtml.common import (
    Div, H1, P, Form, Button, Input, Textarea, Label, Span,
    Section, Aside, Select, Option, A,
)

from user_app.frontend.layout import page_layout, make_step_indicator


def onboarding_page(project):
    """Multi-step wizard that collects BrandMemory fields."""
    mem = project.brand_memory
    pid = project.id

    # Pre-fill values from existing brand_memory if any
    bname = mem.business_name if mem else ""
    tagline = mem.tagline if mem else ""
    wtype = mem.website_type if mem else ""
    goal = mem.primary_goal if mem else ""
    desc = mem.description if mem else ""
    services = ", ".join(mem.services) if mem and mem.services else ""
    email = mem.contact_email if mem else ""
    phone = mem.contact_phone if mem else ""
    address = mem.address if mem else ""

    website_types = [
        ("", "Select a type..."),
        ("portfolio", "Portfolio"),
        ("business", "Business"),
        ("personal", "Personal"),
        ("freelancer", "Freelancer"),
        ("restaurant", "Restaurant"),
        ("nonprofit", "Nonprofit"),
    ]
    goals = [
        ("", "Select a goal..."),
        ("attract_clients", "Attract new clients"),
        ("showcase_work", "Showcase my work"),
        ("provide_info", "Provide information"),
        ("build_credibility", "Build credibility"),
        ("sell_services", "Sell services"),
    ]

    # Step 1: Welcome
    step1 = Section(
        Div(
            H1("Welcome to Okenaba", cls="step-title"),
            P(
                "Let's create your online presence. We'll walk you through it "
                "step by step \u2014 no technical skills needed.",
                cls="step-description",
            ),
            Div(
                Div(cls="welcome-icon-bar"),
                Div(cls="welcome-icon-bar"),
                Div(cls="welcome-icon-bar"),
                cls="welcome-icon",
            ),
            Button("Let's Get Started", cls="button button-primary",
                   type="button", onclick="nextStep()"),
            cls="step-content",
        ),
        id="step1", cls="step step-active",
    )

    # Step 2: Basic Info
    step2 = Section(
        Div(
            H1("Tell Us About You", cls="step-title"),
            P("Start with the basics. You can always refine this later.", cls="step-description"),
            Div(
                Div(
                    Label("Business or personal name", _for="business_name", cls="label"),
                    Input(type="text", name="business_name", id="business_name",
                          value=bname, placeholder="e.g., Sarah's Photography",
                          cls="input", oninput="updatePreview(); clearFieldError(this)"),
                    Span(cls="field-error", id="business_name_error", role="alert"),
                    cls="form-group",
                ),
                Div(
                    Label("Tagline", Span("(optional)", cls="optional"), _for="tagline", cls="label"),
                    Input(type="text", name="tagline", id="tagline",
                          value=tagline, placeholder="e.g., Creating beautiful moments",
                          cls="input", oninput="updatePreview()"),
                    cls="form-group",
                ),
                Div(
                    Label("Website type", _for="website_type", cls="label"),
                    Select(
                        *[Option(lbl, value=val, selected=(val == wtype)) for val, lbl in website_types],
                        name="website_type", id="website_type", cls="input",
                        onchange="clearFieldError(this)",
                    ),
                    Span(cls="field-error", id="website_type_error", role="alert"),
                    cls="form-group",
                ),
                Div(
                    Button("Back", type="button", cls="button button-secondary", onclick="prevStep()"),
                    Button("Next", type="button", cls="button button-primary", onclick="nextStep()"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step2", cls="step",
    )

    # Step 3: Story
    step3 = Section(
        Div(
            H1("Add Your Story", cls="step-title"),
            P("Tell visitors what you're about. Keep it simple and genuine.", cls="step-description"),
            Div(
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
                    Label("Description", Span("(optional)", cls="optional"), _for="description", cls="label"),
                    Textarea(
                        desc,
                        name="description", id="description",
                        placeholder="Tell people about yourself or your business...",
                        cls="input input-textarea", rows="4", oninput="updatePreview()",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Services", Span("(comma separated, optional)", cls="optional"), _for="services", cls="label"),
                    Input(type="text", name="services", id="services",
                          value=services,
                          placeholder="e.g., Photography, Editing, Prints",
                          cls="input"),
                    cls="form-group",
                ),
                Div(
                    Button("Back", type="button", cls="button button-secondary", onclick="prevStep()"),
                    Button("Next", type="button", cls="button button-primary", onclick="nextStep()"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step3", cls="step",
    )

    # Step 4: Contact + submit
    step4 = Section(
        Div(
            H1("How Can People Reach You?", cls="step-title"),
            P("Add your contact info so visitors can get in touch.", cls="step-description"),
            Div(
                Div(
                    Label("Email address", Span("(optional)", cls="optional"), _for="contact_email", cls="label"),
                    Input(type="email", name="contact_email", id="contact_email",
                          value=email, placeholder="your@email.com", cls="input",
                          oninput="updatePreview()"),
                    cls="form-group",
                ),
                Div(
                    Label("Phone", Span("(optional)", cls="optional"), _for="contact_phone", cls="label"),
                    Input(type="text", name="contact_phone", id="contact_phone",
                          value=phone, placeholder="(555) 123-4567", cls="input"),
                    cls="form-group",
                ),
                Div(
                    Label("Address", Span("(optional)", cls="optional"), _for="address", cls="label"),
                    Input(type="text", name="address", id="address",
                          value=address, placeholder="City, State", cls="input"),
                    cls="form-group",
                ),
                Div(
                    Button("Back", type="button", cls="button button-secondary", onclick="prevStep()"),
                    Button("Save & Continue", type="submit", cls="button button-primary",
                           onclick="return validateBeforeSubmit()"),
                    cls="button-group",
                ),
                cls="form",
            ),
            cls="step-content",
        ),
        id="step4", cls="step",
    )

    # Preview panel (desktop sidebar)
    preview = Aside(
        Div(
            Div(Span("Preview", cls="preview-title"), cls="preview-header"),
            Div(
                Div(P("Your site preview will appear here"), cls="preview-placeholder"),
                cls="preview-content", id="previewContent",
            ),
            cls="preview-container",
        ),
        cls="preview-panel",
    )

    form = Form(
        step1, step2, step3, step4,
        # Hidden defaults at form root level
        Input(type="hidden", name="theme", value="professional"),
        Input(type="hidden", name="primary_color", value="#2563eb"),
        Input(type="hidden", name="secondary_color", value="#1e40af"),
        method="post", action=f"/projects/{pid}/memory", cls="wizard",
    )

    # Marker so app.js can detect onboarding and prompt before leaving
    onboarding_marker = Div(id="onboarding-active", style="display:none")

    indicator = make_step_indicator(1, 4)
    return page_layout(onboarding_marker, form, preview, step_indicator=indicator, title="Okenaba - Setup", project_id=pid, active_nav="projects")


def waiting_for_plan_page(project):
    """After memory is saved — prompt to generate plan."""
    pid = project.id
    name = project.brand_memory.business_name if project.brand_memory else "your site"

    content = Section(
        Div(
            Div("\U0001f4cb", cls="step-icon"),
            H1("Ready to Plan Your Site", cls="step-title"),
            P(
                f"Great! We have everything we need about {name}. "
                "Click below to generate a personalized site plan.",
                cls="step-description",
            ),
            Div(
                Form(
                    Button("Generate My Plan", cls="button button-primary", type="submit",
                           onclick="return showLoading('Generating your plan...')"),
                    method="post", action=f"/projects/{pid}/plan",
                ),
                A("Exit", href="/", cls="button button-secondary"),
                cls="button-group",
            ),
            cls="step-content action-page",
        ),
        cls="step",
    )

    return page_layout(content, title="Okenaba - Generate Plan", project_id=pid, active_nav="projects")
