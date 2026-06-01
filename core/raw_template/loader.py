"""Scan the raw template/ folder and return metadata for all templates."""

import re
from pathlib import Path
from functools import lru_cache

_BASE = Path(__file__).parent.parent.parent / "template"

CATEGORY_META = {
    "ecom":       {"icon": "🛍️",  "label": "E-Commerce"},
    "estate":     {"icon": "🏠",   "label": "Real Estate"},
    "fitness":    {"icon": "💪",   "label": "Fitness"},
    "food":       {"icon": "🍽️",  "label": "Food & Drink"},
    "onlinebiz":  {"icon": "💼",   "label": "Online Business"},
    "portfolio":  {"icon": "🎨",   "label": "Portfolio"},
    "technology": {"icon": "💻",   "label": "Technology"},
    "travel":     {"icon": "✈️",  "label": "Travel"},
    "vehicle":    {"icon": "🚗",   "label": "Vehicle"},
}

_THUMB_PRIORITY = ("header", "hero", "banner", "about")


@lru_cache(maxsize=1)
def list_raw_templates() -> list[dict]:
    result = []
    for cat_dir in sorted(_BASE.iterdir()):
        if not cat_dir.is_dir():
            continue
        cat = cat_dir.name
        meta = CATEGORY_META.get(cat, {"icon": "📄", "label": cat.title()})
        for tpl_dir in sorted(cat_dir.iterdir()):
            if not tpl_dir.is_dir() or tpl_dir.name.startswith("."):
                continue
            html = tpl_dir / "index.html"
            if not html.exists():
                continue
            tpl_id = f"{cat}/{tpl_dir.name}"
            result.append({
                "id": tpl_id,
                "category": cat,
                "name": _fmt(tpl_dir.name),
                "meta": meta,
                "html_path": str(html),
                "css_path": str(tpl_dir / "styles.css"),
                "js_path": str(tpl_dir / "main.js"),
                "assets_dir": str(tpl_dir / "assets"),
                "thumb_url": _find_thumb(tpl_dir, tpl_id),
            })
    return result


def get_raw_template(template_id: str) -> dict | None:
    return next((t for t in list_raw_templates() if t["id"] == template_id), None)


@lru_cache(maxsize=128)
def read_template_html(html_path: str) -> str:
    """Cached disk read of a template's index.html — file never changes at runtime."""
    return Path(html_path).read_text(encoding="utf-8", errors="ignore")


_LINK_CSS_RE   = re.compile(r'<link\b[^>]*href=["\'][^"\']*\.css["\'][^>]*/?>(\s*</link>)?', re.IGNORECASE)
_SCRIPT_SRC_RE = re.compile(r'<script\b[^>]*src=["\'][^"\']*["\'][^>]*>\s*</script>', re.IGNORECASE | re.DOTALL)
_CSS_URL_RE    = re.compile(r'url\(["\']?assets/([^"\')\s]+)["\']?\)')
_HTML_SRC_RE   = re.compile(r'(src=["\'])assets/', re.IGNORECASE)
_HTML_HREF_RE  = re.compile(r'(href=["\'])assets/', re.IGNORECASE)
_HTML_SRCSET_RE = re.compile(r'(srcset=["\'])assets/', re.IGNORECASE)


@lru_cache(maxsize=256)
def get_template_srcdoc(tpl_id: str) -> str:
    """
    Return a self-contained HTML string for use as an iframe srcdoc.
    Inlines CSS with absolute asset URLs, rewrites all relative asset
    references to absolute /raw-asset/ paths. Never uses <base> tag —
    srcdoc + <base> is unreliable across browsers.
    Cached forever — template files never change at runtime.
    """
    tpl = get_raw_template(tpl_id)
    if not tpl:
        return "<html><body></body></html>"

    asset_base = f"/raw-asset/{tpl_id}/assets"

    html = read_template_html(tpl["html_path"])

    # Read and inline CSS with absolute asset URLs
    css_path = Path(tpl["css_path"])
    css = ""
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8", errors="ignore")
        css = _CSS_URL_RE.sub(lambda m: f'url("{asset_base}/{m.group(1)}")', css)

    # Strip external stylesheet links and external JS
    html = _LINK_CSS_RE.sub("", html)
    html = _SCRIPT_SRC_RE.sub("", html)

    # Rewrite relative asset references to absolute paths in HTML
    html = _HTML_SRC_RE.sub(   lambda m: f'{m.group(1)}{asset_base}/', html)
    html = _HTML_HREF_RE.sub(  lambda m: f'{m.group(1)}{asset_base}/', html)
    html = _HTML_SRCSET_RE.sub(lambda m: f'{m.group(1)}{asset_base}/', html)

    style_tag = f"<style>{css}</style>" if css else ""

    if "<head>" in html:
        html = html.replace("<head>", f"<head>{style_tag}", 1)
    elif "<HEAD>" in html:
        html = html.replace("<HEAD>", f"<HEAD>{style_tag}", 1)
    else:
        html = f"<html><head>{style_tag}</head><body>" + html + "</body></html>"

    return html


def _find_thumb(tpl_dir: Path, tpl_id: str) -> str | None:
    assets = tpl_dir / "assets"
    if not assets.exists():
        return None
    imgs = [f for f in sorted(assets.iterdir())
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    # Prefer header/hero image
    for priority in _THUMB_PRIORITY:
        for img in imgs:
            if priority in img.stem.lower():
                return f"/raw-asset/{tpl_id}/assets/{img.name}"
    return f"/raw-asset/{tpl_id}/assets/{imgs[0].name}" if imgs else None


def _fmt(name: str) -> str:
    return " ".join(p.title() for p in name.split("_"))
