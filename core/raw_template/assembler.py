"""Assemble the final HTML: inject images, inline CSS/JS, fix asset paths."""

import re
from pathlib import Path
from functools import lru_cache

from core.raw_template.slot_analyzer import detect_slot, _CSS_URL_RE as _SLOT_CSS_URL_RE


@lru_cache(maxsize=128)
def _read_file(path: str) -> str:
    """Cached disk read — template files never change at runtime."""
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

_IMG_SRC_RE = re.compile(
    r'(<img\b[^>]*\bsrc=["\'])assets/([^"\']+)(["\'][^>]*/?>)',
    re.IGNORECASE | re.DOTALL,
)
_ALT_RE    = re.compile(r'\balt=["\']([^"\']*)["\']', re.IGNORECASE)
_LINK_RE   = re.compile(
    r'<link\b[^>]*\bhref=["\'][^"\']*styles\.css["\'][^>]*/?>(\s*</link>)?',
    re.IGNORECASE,
)
_JS_TAG_RE = re.compile(
    r'<script\b[^>]*\bsrc=["\'][^"\']*main\.js["\'][^>]*>\s*</script>',
    re.IGNORECASE,
)


def assemble(
    template: dict,
    rewritten_html: str,
    image_map: dict[str, str],  # {slot_name: uploaded_url}
    base_asset_url: str = "/raw-asset",
    primary_color: str = "",
    secondary_color: str = "",
) -> str:
    """
    1. Replace img src with uploaded URLs or absolute asset routes.
    2. Inline CSS (fix url() references).
    3. Override :root color variables with user's brand colors.
    4. Inline JS.
    5. Return self-contained HTML string.
    """
    html = rewritten_html

    html = _inject_images(html, image_map, template["id"], base_asset_url)
    html = _inline_css(html, template, base_asset_url, image_map)
    if primary_color:
        html = _inject_color_override(html, primary_color, secondary_color)
    html = _inline_js(html, template)

    return html


# ── helpers ────────────────────────────────────────────────────────────────

def _inject_images(html: str, image_map: dict, tpl_id: str, base: str) -> str:
    def _replace(m):
        prefix   = m.group(1)
        filename = m.group(2)
        suffix   = m.group(3)
        alt_m    = _ALT_RE.search(m.group(0))
        alt      = (alt_m.group(1) if alt_m else "").lower()

        # Exact stem match first (e.g. "musthave-3" → user's uploaded photo #3)
        # then fall back to slot-type match (e.g. "musthave" → single upload for all)
        stem = filename.lower().rsplit(".", 1)[0]
        slot = detect_slot(alt, filename)
        url  = image_map.get(stem) or image_map.get(slot) or f"{base}/{tpl_id}/assets/{filename}"
        return f"{prefix}{url}{suffix}"

    return _IMG_SRC_RE.sub(_replace, html)


def _inline_css(html: str, template: dict, base: str, image_map: dict | None = None) -> str:
    css_path = template["css_path"]
    css = _read_file(css_path)
    if not css:
        return html

    def _replace_css_url(m):
        filename = m.group(1)
        if image_map:
            stem = filename.lower().rsplit(".", 1)[0]
            slot = detect_slot("", filename)
            url = image_map.get(stem) or image_map.get(slot)
            if url:
                return f'url("{url}")'
        return f'url("{base}/{template["id"]}/assets/{filename}")'

    css = _SLOT_CSS_URL_RE.sub(_replace_css_url, css)

    # Remove existing external stylesheet links
    html = _LINK_RE.sub("", html)
    # Inject before </head>
    html = html.replace("</head>", f"<style>\n{css}\n</style>\n</head>", 1)
    return html


def _inject_color_override(html: str, primary: str, secondary: str) -> str:
    """Inject a :root override after the inlined stylesheet so brand colors win."""
    dark = secondary if secondary else _darken_hex(primary)
    override = (
        "<style>\n"
        ":root {\n"
        f"  --primary-color: {primary};\n"
        f"  --primary-color-dark: {dark};\n"
        f"  --secondary-color: {dark};\n"
        f"  --accent-color: {primary};\n"
        "}\n"
        "</style>\n"
    )
    return html.replace("</head>", override + "</head>", 1)


def _darken_hex(hex_color: str, factor: float = 0.75) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return "#1e40af"
    r = int(int(h[0:2], 16) * factor)
    g = int(int(h[2:4], 16) * factor)
    b = int(int(h[4:6], 16) * factor)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


def _inline_js(html: str, template: dict) -> str:
    js = _read_file(template["js_path"])
    if not js:
        return html
    html = _JS_TAG_RE.sub("", html)
    html = html.replace("</body>", f"<script>\n{js}\n</script>\n</body>", 1)
    return html
