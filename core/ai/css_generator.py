from pathlib import Path

import anthropic

from config.settings import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from core.models.brand_memory import BrandMemory
from core.ai.schemas import CSSOutput
from core.errors import AIGenerationError, AIValidationError

_PROMPT_PATH = Path(__file__).parent / "prompts" / "css.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()


def _build_prompt(html: str, memory: BrandMemory) -> str:
    return _SYSTEM_PROMPT.format(
        primary_color=memory.primary_color,
        secondary_color=memory.secondary_color,
        theme=memory.theme,
        html_content=html,
    )


def _validate_css(css: str) -> None:
    issues: list[str] = []

    css_lower = css.lower()

    if "@import" in css_lower:
        issues.append("CSS must not contain @import rules")

    if "url(" in css_lower:
        # Allow data: URIs but block external URLs
        import re
        urls = re.findall(r'url\(["\']?(.*?)["\']?\)', css_lower)
        for url in urls:
            if not url.startswith("data:"):
                issues.append(f"CSS must not reference external URLs: {url}")

    if issues:
        raise AIValidationError(issues)


def run_css_generator(html: str, memory: BrandMemory) -> CSSOutput:
    """Call Claude to generate CSS for the given HTML and brand memory."""
    prompt = _build_prompt(html, memory)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise AIGenerationError("css_generator", str(e)) from e

    raw_text = _strip_markdown_fences(response.content[0].text)
    _validate_css(raw_text)
    return CSSOutput(css=raw_text)
