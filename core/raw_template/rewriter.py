"""AI content rewriter — extracts visible text nodes, rewrites via LLM, injects back."""

import re
import json
from openai import OpenAI

from config.settings import HF_API_KEY, HF_BASE_URL, HF_MODELS
from core.models.brand_memory import BrandMemory
from core.errors import AIGenerationError

_SYSTEM = """You are a professional website copywriter.
You receive a JSON object where each key is a placeholder and each value is original website text.
Rewrite each value to match the provided business context.
Return ONLY valid JSON with the same keys and rewritten values.

Rules:
1. Replace all demo/generic text with real copy for this specific business.
2. Never use placeholders like "[Name]", "[Company]", or "[Your Business]".
3. Keep text lengths similar — short texts stay short, long texts stay proportional.
4. Button / CTA text (1–3 words like "SHOP NOW", "GET STARTED", "LEARN MORE") must stay 1–3 words. Never expand a short CTA into a phrase.
5. Return ONLY the JSON object — no markdown fences, no explanation."""

_CODE_BLOCK_RE = re.compile(
    r'<(script|style)\b[^>]*>.*?</\1>',
    re.DOTALL | re.IGNORECASE,
)
_TEXT_NODE_RE = re.compile(r'>([^<>]+)<')
_PLACEHOLDER_RE = re.compile(r'__T\d+__')


def rewrite_html(html: str, memory: BrandMemory) -> str:
    """Extract text nodes, rewrite via LLM, inject back — HTML structure untouched."""
    # Remove code blocks so we don't extract JS/CSS as text
    stripped, code_blocks = _strip_code(html)

    templated, texts = _extract_texts(stripped)

    if not texts:
        return html

    payload = json.dumps(texts, ensure_ascii=False)
    prompt = f"Business Context:\n{_ctx(memory)}\n\nTexts to rewrite:\n{payload}"

    client = OpenAI(base_url=HF_BASE_URL, api_key=HF_API_KEY, max_retries=2)
    try:
        resp = client.chat.completions.create(
            model=HF_MODELS["copy"],
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.35,
            max_tokens=4000,
            timeout=90,
        )
    except Exception as e:
        raise AIGenerationError("content_rewriter", str(e)) from e

    raw = resp.choices[0].message.content or ""
    raw = _clean_fences(raw)

    if not raw.strip():
        raise AIGenerationError("content_rewriter", "LLM returned empty response")

    try:
        rewritten = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AIGenerationError("content_rewriter", f"Invalid JSON: {e}") from e

    result = _restore_texts(templated, rewritten)
    result = _restore_code(result, code_blocks)
    return result


# ── helpers ────────────────────────────────────────────────────────────────

def _strip_code(html: str) -> tuple[str, list[tuple[str, str]]]:
    """Replace script/style blocks with unique tokens; return (stripped, [(token, block)])."""
    blocks: list[tuple[str, str]] = []

    def replacer(m: re.Match) -> str:
        token = f"__CODE{len(blocks)}__"
        blocks.append((token, m.group(0)))
        return token

    stripped = _CODE_BLOCK_RE.sub(replacer, html)
    return stripped, blocks


def _restore_code(html: str, blocks: list[tuple[str, str]]) -> str:
    for token, block in blocks:
        html = html.replace(token, block, 1)
    return html


def _extract_texts(html: str) -> tuple[str, dict[str, str]]:
    """Replace visible text nodes (>text<) with numbered placeholders."""
    texts: dict[str, str] = {}
    idx = [0]

    def replacer(m: re.Match) -> str:
        text = m.group(1)
        stripped = text.strip()
        if len(stripped) < 3:
            return m.group(0)
        key = f"__T{idx[0]}__"
        texts[key] = stripped
        idx[0] += 1
        leading  = text[: len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()) :]
        return f">{leading}{key}{trailing}<"

    result = _TEXT_NODE_RE.sub(replacer, html)
    return result, texts


def _restore_texts(html: str, rewritten: dict) -> str:
    for key, value in rewritten.items():
        if isinstance(value, str) and value.strip():
            html = html.replace(key, value)
    # Drop any placeholders the LLM missed
    html = _PLACEHOLDER_RE.sub("", html)
    return html


def _ctx(m: BrandMemory) -> str:
    return "\n".join([
        f"Business Name: {m.business_name}",
        f"Industry: {', '.join(m.services) if m.services else 'General'}",
        f"Description: {m.description or 'N/A'}",
        f"Primary Goal: {m.primary_goal or 'N/A'}",
        f"Tagline: {m.tagline or 'N/A'}",
        f"Tone: {m.theme or 'professional'}",
        f"Contact Email: {m.contact_email or 'N/A'}",
        f"Contact Phone: {m.contact_phone or 'N/A'}",
        f"Address: {m.address or 'N/A'}",
    ])


def _clean_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        nl = text.find("\n")
        if nl != -1:
            text = text[nl + 1:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
