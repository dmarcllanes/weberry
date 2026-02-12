import json
from pathlib import Path

import anthropic

from config.settings import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from core.models.brand_memory import BrandMemory
from core.ai.schemas import SitePlan, SectionPlan, validate_site_plan
from core.errors import AIGenerationError

_PROMPT_PATH = Path(__file__).parent / "prompts" / "planner.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences if the LLM wrapped its output."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (with optional language tag)
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()


def _build_prompt(memory: BrandMemory) -> str:
    return _SYSTEM_PROMPT.format(
        business_name=memory.business_name,
        website_type=memory.website_type,
        primary_goal=memory.primary_goal,
        description=memory.description,
        tagline=memory.tagline,
        services=", ".join(memory.services) if memory.services else "N/A",
    )


def _parse_response(raw: str) -> SitePlan:
    cleaned = _strip_markdown_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise AIGenerationError("planner", f"Invalid JSON: {e}") from e

    try:
        sections = [
            SectionPlan(
                id=s["id"],
                title=s["title"],
                purpose=s["purpose"],
                content_notes=s["content_notes"],
            )
            for s in data["sections"]
        ]
        plan = SitePlan(
            sections=sections,
            page_title=data["page_title"],
            meta_description=data["meta_description"],
        )
    except (KeyError, TypeError) as e:
        raise AIGenerationError("planner", f"Missing field: {e}") from e

    return plan


def run_planner(memory: BrandMemory) -> SitePlan:
    """Call Claude to generate a site plan from brand memory."""
    prompt = _build_prompt(memory)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise AIGenerationError("planner", str(e)) from e

    raw_text = response.content[0].text
    plan = _parse_response(raw_text)
    validate_site_plan(plan)
    return plan
