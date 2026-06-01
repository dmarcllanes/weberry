"""Serve a raw template as a full-page preview (public, no auth required)."""

from functools import lru_cache
from starlette.responses import HTMLResponse, Response

from core.raw_template.loader import get_raw_template, read_template_html

_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
}


@lru_cache(maxsize=256)
def _build_preview_html(tpl_id: str, html_path: str) -> str:
    """Read + base-tag inject — cached per template, file never changes at runtime."""
    html = read_template_html(html_path)
    base_tag = f'<base href="/raw-asset/{tpl_id}/">'
    if "<head>" in html:
        return html.replace("<head>", f"<head>{base_tag}", 1)
    if "<HEAD>" in html:
        return html.replace("<HEAD>", f"<HEAD>{base_tag}", 1)
    return base_tag + html


def serve(tpl_id: str):
    tpl = get_raw_template(tpl_id)
    if not tpl:
        return Response("Template not found", status_code=404)
    html = _build_preview_html(tpl_id, tpl["html_path"])
    return HTMLResponse(html, headers=_CACHE_HEADERS)
