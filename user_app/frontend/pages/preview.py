"""Preview page (SITE_GENERATED / PREVIEW states)."""

import re
import random
from pathlib import Path

from fasthtml.common import (
    Div, H1, H2, H3, P, Form, Button, Section, Iframe, A, Span,
    Input, Details, Summary, Img, Label, Select, Option,
)

from user_app.frontend.layout import page_layout
from core.ai.template_loader import load_template_manifest

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "templates"

THUMB_SIZE = 300  # square thumbnails


def _friendly_label(slot_name: str) -> str:
    return slot_name.replace("_", " ").title()


def _get_thumb_url(slot_name: str, site_plan) -> str:
    override = site_plan.image_overrides.get(slot_name)
    if override:
        return override
    keyword = site_plan.image_keywords.get(slot_name, slot_name).strip().replace(" ", "-")
    return f"https://picsum.photos/seed/{keyword}/300/200"


def _get_template_slots(template_id: str) -> list[str]:
    """Get all image slot names actually used in the template HTML."""
    template_path = TEMPLATES_DIR / template_id / "template.html"
    if not template_path.exists():
        return []
    html = template_path.read_text()
    # Match all xxx_url variable references inside Jinja2 {{ }} blocks,
    # including conditionals like {{ a_url if ... else b_url }}
    seen = set()
    slots = []
    for m in re.findall(r"(\w+)_url", html):
        if m not in seen:
            seen.add(m)
            slots.append(m)
    return slots


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

    # Get slots actually used in the template HTML
    template_id = project.site_plan.selected_template if project.site_plan else ""
    used_slots = _get_template_slots(template_id) if template_id else []

    # Build image thumbnail cards (image + label + keyword input)
    slot_cards = []
    upload_options = []
    for slot_name in used_slots:
        is_override = slot_name in project.site_plan.image_overrides
        current_keyword = project.site_plan.image_keywords.get(slot_name, "")
        thumb_url = _get_thumb_url(slot_name, project.site_plan)
        friendly = _friendly_label(slot_name)

        badge = (Span("Uploaded", cls="img-editor-badge img-editor-badge--uploaded")
                 if is_override else None)

        keyword_form = Form(
            Input(type="hidden", name="slot_name", value=slot_name),
            Input(type="hidden", name="action", value="keyword"),
            Div(
                Input(type="text", name="keyword", value=current_keyword,
                      placeholder="e.g. coffee, pastry",
                      cls="input input-sm img-editor-kw-input"),
                Button("Update", type="submit", cls="btn btn-sm btn-primary"),
                cls="img-editor-kw-row",
            ),
            method="post", action=f"/projects/{pid}/edit-image",
        )

        header_children = [Span(friendly, cls="img-editor-slot-name")]
        if badge:
            header_children.append(badge)

        # Per-slot upload form
        upload_form_dynamic = Form(
            Input(type="hidden", name="slot_name", value=slot_name),
            Input(type="hidden", name="action", value="upload"),
            Label(
                "Upload Image",
                Input(type="file", name="file", accept="image/*",
                      style="display:none", onchange="this.form.submit()"),
                cls="btn btn-sm btn-outline-primary",
                style="cursor:pointer; width:100%; text-align:center; margin-top:0.5rem; display:block;"
            ),
            method="post", action=f"/projects/{pid}/edit-image",
            enctype="multipart/form-data",
            style="width:100%"
        )

        card = Div(
            Img(src=thumb_url, alt=friendly, cls="img-editor-thumb"),
            Div(
                Div(*header_children, cls="img-editor-card-header"),
                keyword_form,
                upload_form_dynamic,
                cls="img-editor-card-body",
            ),
            cls="img-editor-card",
        )
        slot_cards.append(card)
        upload_options.append(Option(friendly, value=slot_name))

    # Single upload form at the bottom
    upload_form = Form(
        Input(type="hidden", name="action", value="upload"),
        Div(
            Div(
                Label("Choose image slot", cls="img-editor-field-label"),
                Select(*upload_options, name="slot_name", cls="input input-sm"),
                cls="img-editor-upload-field",
            ),
            Div(
                Label("Select file", cls="img-editor-field-label"),
                Input(type="file", name="file", accept="image/*",
                      cls="input input-sm", style="font-size:0.85rem"),
                cls="img-editor-upload-field",
            ),
            Button("Upload Image", type="submit", cls="btn btn-primary",
                   style="align-self:flex-end"),
            cls="img-editor-upload-row",
        ),
        method="post", action=f"/projects/{pid}/edit-image",
        enctype="multipart/form-data",
    ) if upload_options else Div()

    # Image editor section — open by default
    image_editor = Details(
        Summary("Edit Images", cls="img-editor-summary"),
        Div(
            P("Change images by entering a keyword, or upload your own below.",
              cls="img-editor-hint"),
            Div(*slot_cards, cls="img-editor-grid"),
            Div(
                H3("Upload Your Own Image", cls="img-editor-upload-title"),
                upload_form,
                cls="img-editor-upload-section",
            ),
        ),
        open=True,
        cls="img-editor-section",
    ) if slot_cards else Div()

    content = Section(
        Div(
            H1("Preview Your Site", cls="step-title"),
            P(
                "Here's your generated website. Review it below, then publish when ready.",
                cls="step-description",
            ),
            Div(
                browser_bar,
                Iframe(
                    src=f"/projects/{pid}/preview-render",
                    cls="site-preview-frame",
                    title="Site preview",
                    style="width:100%;height:600px;border:none;border-radius:0 0 8px 8px",
                ),
                cls="browser-chrome",
            ),
            Div(
                A("Back to Projects", href="/", cls="button button-secondary"),
                A("Edit Content", href=f"/projects/{pid}/edit", cls="button button-secondary"),
                Form(
                    Button("Publish My Site", cls="button button-primary", type="submit",
                           onclick="return showLoading('Publishing your site...')"),
                    method="post", action=f"/projects/{pid}/publish",
                ),
                cls="button-group",
                style="margin-top:var(--spacing-lg)",
            ),
            image_editor,
            cls="step-content",
        ),
        cls="step",
        style="max-width:960px;margin:0 auto;padding:2rem",
    )

    return page_layout(content, user=user, title="Okenaba - Preview", project_id=pid, active_nav="projects")
