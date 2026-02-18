import re

from core.errors import AIValidationError


def validate_for_publish(html: str, css: str) -> None:
    """Re-run safety checks before publishing. Must pass all checks."""
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

    css_lower = css.lower()

    if "@import" in css_lower:
        issues.append("CSS must not contain @import rules")

    urls = re.findall(r'url\(["\']?(.*?)["\']?\)', css_lower)
    for url in urls:
        # Allow data URIs, local paths, and HTTPS (Supabase uploads, picsum)
        if url.startswith(("data:", "/", "https://")):
            continue
        issues.append(f"CSS must not reference external URLs: {url}")

    if issues:
        raise AIValidationError(issues)
