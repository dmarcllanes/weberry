"""Parse a raw HTML template and return image slot requirements."""

import re
from pathlib import Path
from functools import lru_cache

_SIZE_MAP = {
    "header":    ("1200 × 600 px", "landscape"),
    "hero":      ("1200 × 600 px", "landscape"),
    "banner":    ("1200 × 400 px", "landscape"),
    "about":     ("600 × 400 px",  "landscape"),
    "product":   ("400 × 400 px",  "square"),
    "gallery":   ("600 × 400 px",  "landscape"),
    "discover":  ("600 × 400 px",  "landscape"),
    "article":   ("600 × 400 px",  "landscape"),
    "subscribe": ("1200 × 400 px", "landscape"),
    "team":      ("300 × 300 px",  "square"),
    "popular":   ("300 × 300 px",  "square"),
    "icon":      ("80 × 80 px",    "square"),
    "logo":      ("200 × 80 px",   "landscape"),
    "work":      ("600 × 400 px",  "landscape"),
    "mission":   ("600 × 400 px",  "landscape"),
    "property":  ("600 × 400 px",  "landscape"),
    "slide":     ("1200 × 600 px", "landscape"),
    "car":       ("800 × 500 px",  "landscape"),
    "vehicle":   ("800 × 500 px",  "landscape"),
    "service":   ("400 × 300 px",  "landscape"),
    "review":    ("80 × 80 px",    "square"),
    "blog":      ("600 × 400 px",  "landscape"),
    "portfolio": ("600 × 400 px",  "landscape"),
    "room":      ("600 × 400 px",  "landscape"),
    "meal":      ("400 × 400 px",  "square"),
    "food":      ("400 × 400 px",  "square"),
    "drink":     ("400 × 400 px",  "square"),
    "place":     ("600 × 400 px",  "landscape"),
    "dest":      ("600 × 400 px",  "landscape"),
}

_IMG_RE = re.compile(
    r'<img\b[^>]*\bsrc=["\']assets/([^"\']+)["\'][^>]*/?>',
    re.IGNORECASE | re.DOTALL,
)
_ALT_RE = re.compile(r'\balt=["\']([^"\']*)["\']', re.IGNORECASE)
_TRAIL_RE = re.compile(r'[-_]\d+$')
_CSS_URL_RE = re.compile(r'url\(["\']?assets/([^"\')\s]+)["\']?\)', re.IGNORECASE)


@lru_cache(maxsize=64)
def analyze_slots(html_path: str) -> list[dict]:
    """Return list of image slot dicts, one per unique slot type found in the HTML and CSS."""
    html = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    slots: dict[str, dict] = {}
    seen_filenames: set[str] = set()

    def _add(filename: str, alt: str = "") -> None:
        if filename in seen_filenames:
            return
        seen_filenames.add(filename)
        slot = detect_slot(alt, filename)
        size, orient = _SIZE_MAP.get(slot, ("800 × 600 px", "landscape"))
        if slot not in slots:
            slots[slot] = {
                "slot":  slot,
                "label": slot.replace("-", " ").title() + " Image",
                "count": 0,
                "filenames": [],
                "recommended_size": size,
                "orientation": orient,
            }
        slots[slot]["count"] += 1
        slots[slot]["filenames"].append(filename)

    # Scan <img src="assets/..."> in HTML
    for m in _IMG_RE.finditer(html):
        filename = m.group(1)
        alt_m = _ALT_RE.search(m.group(0))
        alt = (alt_m.group(1) if alt_m else "").lower().strip()
        _add(filename, alt)

    # Scan url(assets/...) in styles.css (catches CSS background images)
    css_path = Path(html_path).parent / "styles.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8", errors="ignore")
        for m in _CSS_URL_RE.finditer(css):
            _add(m.group(1))

    return list(slots.values())


def detect_slot(alt: str, filename: str) -> str:
    """Infer slot type from alt text or filename."""
    stem = filename.lower().rsplit(".", 1)[0]
    stem = _TRAIL_RE.sub("", stem)

    for candidate in (alt, stem):
        for kw in _SIZE_MAP:
            if kw in candidate:
                return kw

    return stem if stem else "image"
