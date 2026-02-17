"""AI copy writer: picks template, writes copy, decides active sections."""

import json
from pathlib import Path

from openai import OpenAI

from config.settings import HF_API_KEY, HF_MODELS, HF_BASE_URL
from core.models.brand_memory import BrandMemory
from core.ai.schemas import SitePlan, SectionPlan, CopyBlock
from core.errors import AIGenerationError

_PROMPT_PATH = Path(__file__).parent / "prompts" / "copy_writer.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _build_prompt(memory: BrandMemory, templates_summary: str) -> str:
    return _SYSTEM_PROMPT.format(
        business_name=memory.business_name,
        tagline=memory.tagline or "N/A",
        website_type=memory.website_type,
        primary_goal=memory.primary_goal,
        description=memory.description or "N/A",
        services=", ".join(memory.services) if memory.services else "N/A",
        project_intent=memory.project_intent.value if hasattr(memory.project_intent, "value") else str(memory.project_intent),
        theme=memory.theme or "professional",
        contact_email=memory.contact_email or "N/A",
        contact_phone=memory.contact_phone or "N/A",
        address=memory.address or "N/A",
        labeled_assets=str([{"label": a.label, "orientation": a.orientation, "width": a.width, "height": a.height} for a in memory.labeled_assets])
        if memory.labeled_assets else "None",
        templates_summary=templates_summary,
    )


def _parse_response(raw: str) -> dict:
    cleaned = _strip_markdown_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise AIGenerationError("copy_writer", f"Invalid JSON: {e}") from e


def run_copy_writer(memory: BrandMemory, templates_summary: str) -> SitePlan:
    """Call LLM to pick template + write copy. Returns a SitePlan with copy_blocks."""
    prompt = _build_prompt(memory, templates_summary)

    client = OpenAI(base_url=HF_BASE_URL, api_key=HF_API_KEY, max_retries=5)
    try:
        response = client.chat.completions.create(
            model=HF_MODELS["copy"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
        )
    except Exception as e:
        raise AIGenerationError("copy_writer", str(e)) from e

    raw_text = response.choices[0].message.content
    data = _parse_response(raw_text)

    try:
        copy_blocks = [
            CopyBlock(placeholder_key=cb["key"], content=cb["content"])
            for cb in data.get("copy_blocks", [])
        ]

        # Build minimal SectionPlan list from active sections (for compatibility)
        sections = [
            SectionPlan(id=s, title=s.replace("_", " ").title(), purpose="", content_notes="")
            for s in data.get("active_sections", [])
        ]

        plan = SitePlan(
            sections=sections,
            page_title=data.get("page_title", memory.business_name),
            meta_description=data.get("meta_description", ""),
            copy_blocks=copy_blocks,
            active_sections=data.get("active_sections", []),
            selected_template=data.get("selected_template", ""),
            image_keywords=data.get("image_keywords", {}),
        )
    except (KeyError, TypeError) as e:
        raise AIGenerationError("copy_writer", f"Missing field: {e}") from e

    # Store extra lists (features, testimonials, etc.) in copy_blocks for template rendering
    for list_key in ("features_list", "services_list", "testimonials_list", "faq_list"):
        if list_key in data and data[list_key]:
            plan.copy_blocks.append(
                CopyBlock(placeholder_key=list_key, content=json.dumps(data[list_key]))
            )

    return plan
