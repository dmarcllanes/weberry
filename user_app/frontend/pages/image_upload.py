"""Image upload page — tabbed by slot category, one card per image position."""

from pathlib import Path
from fasthtml.common import (
    Div, H1, H3, P, Span, Form, Button, Input, Img, Section, Script, Safe,
)
from user_app.frontend.layout import page_layout
from core.raw_template.loader import get_raw_template
from core.raw_template.slot_analyzer import analyze_slots


def _img_dims(asset_path: str) -> str | None:
    """Return 'W × H px' string for a template asset, or None on failure."""
    try:
        from PIL import Image as PILImage
        img = PILImage.open(asset_path)
        return f"{img.width} × {img.height} px"
    except Exception:
        return None


_SLOT_NAMES = {
    "header":    "Main Banner",
    "hero":      "Hero Photo",
    "banner":    "Banner",
    "about":     "About Us",
    "product":   "Product",
    "gallery":   "Gallery",
    "discover":  "Discover",
    "article":   "Article",
    "subscribe": "Newsletter",
    "team":      "Team",
    "popular":   "Popular Item",
    "icon":      "Icon",
    "logo":      "Logo",
    "work":      "Work",
    "mission":   "Mission",
    "property":  "Property",
    "slide":     "Slide",
    "car":       "Car",
    "vehicle":   "Vehicle",
    "service":   "Service",
    "review":    "Review",
    "blog":      "Blog",
    "portfolio": "Portfolio",
    "room":      "Room",
    "meal":      "Meal",
    "food":      "Food",
    "drink":     "Drink",
    "place":     "Place",
    "dest":      "Destination",
    "collection": "Collection",
    "sale":       "Sale",
    "musthave":   "Featured",
    "news":       "News",
    "brand":      "Brand Logo",
    "instagram":  "Social",
}

_ORIENT_HINT = {
    "landscape": "Wide photo",
    "square":    "Square photo",
    "portrait":  "Tall photo",
}


def image_upload_page(user, project) -> object:
    tpl   = get_raw_template(project.template_id) if project.template_id else None
    slots = analyze_slots(tpl["html_path"]) if tpl else []

    # Already-uploaded stems
    uploaded = {}
    if project.brand_memory and project.brand_memory.labeled_assets:
        uploaded = {a.label: a.url for a in project.brand_memory.labeled_assets}

    tpl_name = tpl["name"] if tpl else "Your Template"
    tpl_meta = tpl["meta"] if tpl else {"icon": "📄", "label": "Template"}
    tpl_id   = tpl["id"] if tpl else ""

    # Build category groups
    tpl_base = Path(tpl["html_path"]).parent if tpl else Path(".")
    groups = []
    for slot in slots:
        cat_name = _SLOT_NAMES.get(slot["slot"], slot["slot"].title())
        hint     = _ORIENT_HINT.get(slot["orientation"], "")
        done_count = sum(
            1 for fname in slot["filenames"]
            if fname.rsplit(".", 1)[0] in uploaded
        )
        images = []
        for i, fname in enumerate(slot["filenames"]):
            stem       = fname.rsplit(".", 1)[0]
            asset_path = tpl_base / "assets" / fname
            dims       = _img_dims(str(asset_path))
            title      = f"{cat_name} {i + 1}" if slot["count"] > 1 else cat_name
            images.append({
                "stem":     stem,
                "title":    title,
                "hint":     hint,
                "dims":     dims,
                "preview":  f"/raw-asset/{tpl_id}/assets/{fname}",
                "done":     stem in uploaded,
                "done_url": uploaded.get(stem),
            })
        groups.append({
            "id":         slot["slot"],
            "name":       cat_name,
            "count":      slot["count"],
            "done_count": done_count,
            "images":     images,
        })

    first_id = groups[0]["id"] if groups else ""

    content = Section(
        # ── Header ────────────────────────────────────────────────────────
        Div(
            Span(f"{tpl_meta['icon']} {tpl_meta['label']}", cls="ob-cat-badge"),
            H1("Add Your Photos", cls="step-title"),
            P(
                "Pick a category below, then swap any photo with your own — "
                "or keep the template's default.",
                cls="step-description",
            ),
            cls="img-upload-top",
        ),

        Form(
            # ── Category tab strip ────────────────────────────────────────
            Div(
                *[_tab_btn(g, g["id"] == first_id) for g in groups],
                cls="isc-tabs",
                id="isc-tabs",
            ),

            # ── Category panels ───────────────────────────────────────────
            Div(
                *[_category_panel(g, g["id"] == first_id) for g in groups],
                cls="isc-panels",
            ),

            Input(type="hidden", name="upload_step_done", value="1"),

            Div(
                Button(
                    Safe("Continue →"),
                    type="submit",
                    cls="button button-primary img-upload-cta",
                ),
                Button(
                    "Skip — keep all template photos",
                    type="submit", name="skip", value="1",
                    cls="button button-ghost img-upload-skip",
                ),
                cls="img-upload-actions",
            ),

            method="post",
            action=f"/pages/{project.id}/upload",
            enctype="multipart/form-data",
            cls="img-upload-form",
        ),

        # ── JS ────────────────────────────────────────────────────────────
        Script(Safe("""
(function () {
  // Tab switching
  var tabs   = document.querySelectorAll('.isc-tab-btn');
  var panels = document.querySelectorAll('.isc-panel');

  tabs.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = btn.dataset.cat;
      tabs.forEach(function(t) { t.classList.toggle('active', t.dataset.cat === target); });
      panels.forEach(function(p) { p.classList.toggle('active', p.dataset.cat === target); });
    });
  });

  // Keep / Upload toggle per card
  function initCard(card) {
    var keepBtn  = card.querySelector('.isc-keep');
    var ownBtn   = card.querySelector('.isc-upload');
    var zone     = card.querySelector('.isc-zone');
    if (!keepBtn || !ownBtn || !zone) return;

    var inp = zone.querySelector('input[type="file"]');
    var fn  = zone.querySelector('.isc-fname');

    function choose(own) {
      ownBtn.classList.toggle('active', own);
      keepBtn.classList.toggle('active', !own);
      zone.classList.toggle('visible', own);
      if (!own && inp) { inp.value = ''; if (fn) fn.textContent = ''; }
    }
    choose(false);
    keepBtn.addEventListener('click', function(e) { e.preventDefault(); choose(false); });
    ownBtn.addEventListener('click',  function(e) { e.preventDefault(); choose(true);  });

    if (inp) {
      inp.addEventListener('change', function() {
        if (fn) fn.textContent = inp.files[0] ? inp.files[0].name : '';
      });
    }
    zone.addEventListener('dragover',  function(e) { e.preventDefault(); zone.classList.add('drag'); });
    zone.addEventListener('dragleave', function()  { zone.classList.remove('drag'); });
    zone.addEventListener('drop', function(e) {
      e.preventDefault(); zone.classList.remove('drag');
      if (inp && e.dataTransfer.files.length) {
        inp.files = e.dataTransfer.files;
        inp.dispatchEvent(new Event('change'));
      }
    });
    zone.addEventListener('click', function(e) { if (e.target !== inp && inp) inp.click(); });
  }

  document.querySelectorAll('.img-slot-card').forEach(initCard);
})();
""")),

        cls="step img-upload-page",
    )

    return page_layout(content, user=user, title=f"Add Photos — {tpl_name}")


# ── Tab button ───────────────────────────────────────────────────────────────

def _tab_btn(group: dict, active: bool) -> Button:
    done  = group["done_count"]
    total = group["count"]
    badge = Span(f"{done}/{total}", cls="isc-tab-badge isc-tab-badge--done" if done else "isc-tab-badge") if total > 1 else (
        Span("✓", cls="isc-tab-badge isc-tab-badge--done") if done else Span("")
    )
    return Button(
        group["name"],
        badge,
        cls=f"isc-tab-btn{'  active' if active else ''}",
        type="button",
        **{"data-cat": group["id"]},
    )


# ── Category panel ───────────────────────────────────────────────────────────

def _category_panel(group: dict, active: bool) -> Div:
    return Div(
        Div(
            *[_img_card(img) for img in group["images"]],
            cls="img-slot-grid",
        ),
        cls=f"isc-panel{'  active' if active else ''}",
        **{"data-cat": group["id"]},
    )


# ── Individual image card ────────────────────────────────────────────────────

def _img_card(img: dict) -> Div:
    preview = img["done_url"] or img["preview"]

    return Div(
        Div(
            *([Img(src=preview, alt=img["title"], cls="isc-preview-img")] if preview else
              [Div(Span("🖼", style="font-size:2rem"), cls="isc-preview-placeholder")]),
            *(
                [Span("✓ Updated", cls="isc-preview-badge")]
                if img["done"] else []
            ),
            cls="isc-preview",
        ),

        Div(
            H3(img["title"], cls="isc-title"),

            # Recommended size box
            Div(
                Span("📐", cls="isc-size-icon"),
                Div(
                    Span("Recommended size:", cls="isc-size-label"),
                    Span(img.get("dims") or "—", cls="isc-size-value"),
                    *(
                        [Span(f"· {img['hint']}", cls="isc-size-hint")]
                        if img.get("hint") else []
                    ),
                    cls="isc-size-text",
                ),
                cls="isc-size-box",
            ),

            Div(
                Button("Keep template photo", cls="isc-keep active", type="button"),
                Button("Use my own", cls="isc-upload", type="button"),
                cls="isc-choice",
            ),

            Div(
                Span("📂", cls="isc-zone-icon"),
                P("Drop photo here or click to browse", cls="isc-zone-label"),
                Input(
                    type="file",
                    name=f"img_{img['stem']}",
                    accept="image/jpeg,image/png,image/webp",
                    cls="isc-file-input",
                ),
                Span("", cls="isc-fname"),
                cls="isc-zone",
            ),

            cls="isc-body",
        ),

        cls="img-slot-card",
    )
