from pathlib import Path

from openai import OpenAI

from config.settings import HF_API_KEY, HF_MODELS, HF_BASE_URL
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
        # Allow data URIs, local paths, and HTTPS (uploads, picsum)
        import re
        urls = re.findall(r'url\(["\']?(.*?)["\']?\)', css_lower)
        for url in urls:
            if url.startswith(("data:", "/", "https://")):
                continue
            issues.append(f"CSS must not reference external URLs: {url}")

    if issues:
        raise AIValidationError(issues)


def run_css_generator(html: str, memory: BrandMemory) -> CSSOutput:
    """Call LLM via HF Inference (Qwen2.5) to generate CSS."""
    prompt = _build_prompt(html, memory)

    client = OpenAI(base_url=HF_BASE_URL, api_key=HF_API_KEY, max_retries=5)
    try:
        response = client.chat.completions.create(
            model=HF_MODELS["code"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
        )
    except Exception as e:
        raise AIGenerationError("css_generator", str(e)) from e

    raw_text = _strip_markdown_fences(response.choices[0].message.content)
    _validate_css(raw_text)
    return CSSOutput(css=raw_text)
