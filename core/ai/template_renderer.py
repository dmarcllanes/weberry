"""Jinja2 template renderer — no LLM call, pure Python."""

import json
import re
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.ai.schemas import SitePlan
from core.ai.template_loader import load_template_manifest
from core.models.brand_memory import BrandMemory
from core.models.site_version import SiteVersion

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@lru_cache(maxsize=None)
def _get_jinja_env(template_dir: str) -> Environment:
    """Return a cached Jinja2 Environment for a given template directory."""
    return Environment(loader=FileSystemLoader(template_dir), autoescape=False)


@lru_cache(maxsize=None)
def _scan_extra_slots(template_id: str) -> dict:
    """Scan template HTML for _url references not declared in the manifest."""
    template_html_path = TEMPLATES_DIR / template_id / "template.html"
    extra: dict = {}
    if template_html_path.exists():
        html_source = template_html_path.read_text()
        for match in re.findall(r"\{\{\s*(\w+)_url\s*\}\}", html_source):
            extra[match] = "landscape"
    return extra


def render_template(template_id: str, site_plan: SitePlan, memory: BrandMemory) -> SiteVersion:
    """Render a template using Jinja2 with AI-written copy + brand memory data."""
    template_dir = TEMPLATES_DIR / template_id
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory '{template_id}' not found")

    env = _get_jinja_env(str(template_dir))

    # Build context dict from copy_blocks
    context = {}
    list_keys = {"features_list", "services_list", "testimonials_list", "faq_list"}
    for cb in site_plan.copy_blocks:
        if cb.placeholder_key in list_keys:
            try:
                context[cb.placeholder_key] = json.loads(cb.content)
            except (json.JSONDecodeError, TypeError):
                context[cb.placeholder_key] = []
        else:
            context[cb.placeholder_key] = cb.content

    # Inject 'copy' dict for templates that prefer {{ copy.variable }} syntax
    context["copy"] = context.copy()

    # Add active section flags (section_features, section_testimonials, etc.)
    for section in site_plan.active_sections:
        context[f"section_{section}"] = True

    # Add brand memory fields
    context["business_name"] = memory.business_name
    context["tagline"] = memory.tagline or ""
    context["contact_email"] = memory.contact_email or ""
    context["contact_phone"] = memory.contact_phone or ""
    context["address"] = memory.address or ""
    context["primary_color"] = memory.primary_color or "#2563eb"
    context["secondary_color"] = memory.secondary_color or "#1e40af"
    context["page_title"] = site_plan.page_title
    context["meta_description"] = site_plan.meta_description

    # Load manifest to identify image slots (cached)
    try:
        manifest = load_template_manifest(template_id)
        slots = dict(manifest.get("slots", {}))  # copy — never mutate the cached dict
        default_keywords = manifest.get("keywords", ["business"])
    except FileNotFoundError:
        slots = {}
        default_keywords = ["business"]

    # Merge any extra _url references found in the template HTML (cached scan)
    for slot_name, slot_type in _scan_extra_slots(template_id).items():
        if slot_name not in slots:
            slots[slot_name] = slot_type

    # Generate image URLs for each slot or use overrides
    for slot_name, slot_type in slots.items():
        # 1. Uploaded image override takes highest priority
        override_url = site_plan.image_overrides.get(slot_name)
        if override_url:
            context[f"{slot_name}_url"] = override_url
            continue

        # Orientation-based sizing
        if slot_type == "landscape":
            w, h = 1600, 900
        elif slot_type == "portrait":
            w, h = 900, 1600
        elif slot_type == "square":
            w, h = 800, 800
        else:
            w, h = 1200, 800

        # 2. Use user-entered keyword, or deterministically pick from manifest defaults
        keyword = site_plan.image_keywords.get(slot_name)
        if not keyword:
            if default_keywords:
                # Use slot name hash so each slot gets a stable default keyword
                keyword = default_keywords[hash(slot_name) % len(default_keywords)]
            else:
                keyword = slot_name
        keyword_safe = keyword.strip().replace(" ", "-")
        url = f"https://picsum.photos/seed/{keyword_safe}/{w}/{h}"

        context[f"{slot_name}_url"] = url

    # Legacy fallback (optional): if user HAS uploaded assets, override? 
    # For now, Online-First means we ignore old labeled_assets for the initial generation.
    # We can re-introduce them later if needed.

    # Render HTML
    html_template = env.get_template("template.html")
    html = html_template.render(**context)

    # NOTE: Nav hamburger JS is injected at serving time (preview_render / render_final_page)
    # to keep stored HTML free of <script> tags and pass publish validation.

    # Render CSS
    css = ""
    css_path = template_dir / "style.css"
    if css_path.exists():
        css_template = env.get_template("style.css")
        css = css_template.render(**context)

    return SiteVersion(html=html, css=css, version=1)
