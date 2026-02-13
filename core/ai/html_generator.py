import json
import re
from pathlib import Path

from openai import OpenAI

from config.settings import NVIDIA_API_KEY, NVIDIA_MODEL, NVIDIA_BASE_URL
from core.models.brand_memory import BrandMemory
from core.ai.schemas import SitePlan, HTMLOutput
from core.errors import AIGenerationError, AIValidationError

_PROMPT_PATH = Path(__file__).parent / "prompts" / "html.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()


def _build_prompt(plan: SitePlan, memory: BrandMemory) -> str:
    plan_dict = {
        "page_title": plan.page_title,
        "meta_description": plan.meta_description,
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "purpose": s.purpose,
                "content_notes": s.content_notes,
            }
            for s in plan.sections
        ],
    }

    return _SYSTEM_PROMPT.format(
        business_name=memory.business_name,
        website_type=memory.website_type,
        tagline=memory.tagline,
        description=memory.description,
        services=", ".join(memory.services) if memory.services else "N/A",
        contact_email=memory.contact_email or "N/A",
        contact_phone=memory.contact_phone or "N/A",
        address=memory.address or "N/A",
        primary_color=memory.primary_color,
        secondary_color=memory.secondary_color,
        site_plan_json=json.dumps(plan_dict, indent=2),
    )


def _strip_style_tags(html: str) -> str:
    """Remove any <style>...</style> blocks the model included despite instructions."""
    return re.sub(r"<style[\s>].*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)


def _validate_html(html: str) -> None:
    issues: list[str] = []

    html_lower = html.lower()

    if "<script" in html_lower:
        issues.append("HTML must not contain <script> tags")

    if "onclick" in html_lower or "onerror" in html_lower or "onload" in html_lower:
        issues.append("HTML must not contain inline event handlers")

    if "<nav" not in html_lower:
        issues.append("HTML must contain a <nav> element")

    if "<footer" not in html_lower:
        issues.append("HTML must contain a <footer> element")

    if "<!doctype html>" not in html_lower:
        issues.append("HTML must start with <!DOCTYPE html>")

    if issues:
        raise AIValidationError(issues)


def run_html_generator(plan: SitePlan, memory: BrandMemory) -> HTMLOutput:
    """Call LLM via OpenRouter to generate HTML from a site plan and brand memory."""
    prompt = _build_prompt(plan, memory)

    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY, max_retries=5)
    try:
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise AIGenerationError("html_generator", str(e)) from e

    raw_text = _strip_markdown_fences(response.choices[0].message.content)
    raw_text = _strip_style_tags(raw_text)
    _validate_html(raw_text)
    return HTMLOutput(html=raw_text)
