"""Template picker — user browses 9 categories and selects a raw HTML template."""

from fasthtml.common import (
    Div, H1, H3, P, A, Span, Form, Button, Input, Img, Script, Safe, Iframe,
)

from core.raw_template.loader import list_raw_templates, CATEGORY_META, get_template_srcdoc
from user_app.frontend.layout import sidebar_layout


def _template_card(t: dict, show_new: bool) -> Div:
    cat      = t["category"]
    meta     = t["meta"]
    thumb    = t["thumb_url"]
    card_cls = "tpl-card tpl-card--selectable" if show_new else "tpl-card tpl-card--locked"

    thumb_el = Div(
        Iframe(
            srcdoc=get_template_srcdoc(t["id"]),  # inline HTML — zero extra HTTP requests
            cls="tpl-card-iframe",
            tabindex="-1",
            scrolling="no",
            title=t["name"],
            sandbox="allow-same-origin",
        ),
        cls="tpl-iframe-wrap",
    )

    preview_url = f"/tpl-preview/{t['id']}"

    return Div(
        Div(
            thumb_el,
            Span(f"{meta['icon']} {meta['label']}", cls="tpl-card-badge"),
            Div("✓", cls="tpl-card-checkmark"),
            cls="tpl-card-thumb",
        ),
        Div(
            H3(t["name"], cls="tpl-card-name"),
            Div(
                Span(
                    "Tap to select →" if show_new else "🔒 Locked",
                    cls="tpl-card-hint" + ("" if show_new else " tpl-card-hint--locked"),
                ),
                A("👁 View", href=preview_url, target="_blank",
                  cls="tpl-card-view-link", onclick="event.stopPropagation()"),
                cls="tpl-card-footer",
            ),
            cls="tpl-card-body",
        ),
        cls=card_cls,
        data_category=cat,
        data_id=t["id"] if show_new else "",
        data_name=t["name"],
        data_cat_label=f"{meta['icon']} {meta['label']}",
        data_thumb=thumb or "",
        data_preview_url=preview_url,
    )


def _preview_tray() -> Div:
    return Div(
        Div("×", cls="tpl-tray-close", onclick="closeTray()"),
        Div(
            Div(
                Img(id="tray-img", src="", alt="", cls="tpl-tray-img"),
                Span("", id="tray-badge", cls="tpl-tray-badge"),
                cls="tpl-tray-thumb",
            ),
            Div(
                H3("", id="tray-name", cls="tpl-tray-name"),
                P("Choose this template to start building your site.", cls="tpl-tray-desc"),
                cls="tpl-tray-info",
            ),
            Div(
                Form(
                    Input(type="hidden", name="preferred_template_id",
                          id="tray-input", value=""),
                    Button("Start Building →", type="submit",
                           cls="button button-primary tpl-tray-btn"),
                    method="post", action="/pages",
                ),
                A("👁 Preview template", href="#", id="tray-preview-link",
                  target="_blank", cls="tpl-tray-preview-link"),
                cls="tpl-tray-action",
            ),
            cls="tpl-tray-inner",
        ),
        cls="tpl-preview-tray",
        id="tpl-preview-tray",
    )


def template_picker_page(user, show_new: bool = True) -> object:
    templates  = list_raw_templates()
    categories = list(dict.fromkeys(t["category"] for t in templates))
    total      = len(templates)

    # ── Page header (aligned with dashboard pc-page-header pattern) ────────
    header = Div(
        Div(
            H1("Choose Your Template", cls="step-title", style="margin:0"),
            P(
                "Pick the design that fits your business. "
                "The AI rewrites all the content — your design stays exactly as chosen.",
                cls="picker-subtitle",
            ),
            cls="picker-header-text",
        ),
        Span(f"{total} templates", cls="picker-count"),
        cls="picker-header",
    )

    # ── Category tabs in a horizontally-scrollable container ───────────────
    tabs = Div(
        Div(
            A("All", href="#", cls="picker-tab picker-tab--active", data_filter="all"),
            *[
                A(
                    CATEGORY_META.get(c, {}).get("icon", "📄"),
                    " ",
                    CATEGORY_META.get(c, {}).get("label", c.title()),
                    href="#",
                    cls="picker-tab",
                    data_filter=c,
                )
                for c in categories
            ],
            cls="picker-tabs",
        ),
        cls="picker-tabs-scroll",
    )

    cards = [_template_card(t, show_new) for t in templates]

    content = Div(
        header,
        tabs,
        Div(*cards, cls="tpl-grid", id="tpl-grid"),
        cls="picker-content",
    )

    picker_js = Script(Safe("""
(function () {
  // Scale one iframe wrap to fill its card thumbnail area
  function scaleWrap(wrap) {
    var iframe = wrap.querySelector('.tpl-card-iframe');
    if (!iframe) return;
    var w     = wrap.offsetWidth  || 1;
    var h     = wrap.offsetHeight || 200;
    var scale = w / 1280;
    iframe.style.width           = '1280px';
    iframe.style.height          = Math.ceil(h / scale) + 'px';
    iframe.style.transform       = 'scale(' + scale + ')';
    iframe.style.transformOrigin = 'top left';
  }

  function scaleAll() {
    document.querySelectorAll('.tpl-iframe-wrap').forEach(scaleWrap);
  }

  // Scale immediately (srcdoc iframes render synchronously)
  scaleAll();

  // Re-scale after each iframe's load event (images inside may shift layout)
  document.querySelectorAll('.tpl-card-iframe').forEach(function (iframe) {
    iframe.addEventListener('load', function () {
      scaleWrap(iframe.parentElement);
    });
  });

  window.addEventListener('resize', scaleAll);
})();

document.addEventListener('DOMContentLoaded', function () {
    var tray            = document.getElementById('tpl-preview-tray');
    var trayImg         = document.getElementById('tray-img');
    var trayBadge       = document.getElementById('tray-badge');
    var trayName        = document.getElementById('tray-name');
    var trayInput       = document.getElementById('tray-input');
    var trayPreviewLink = document.getElementById('tray-preview-link');
    var mainEl          = document.querySelector('.sidebar-main');

    if (!tray) return;

    function openTray(card) {
        trayImg.src           = card.dataset.thumb      || '';
        trayBadge.textContent = card.dataset.catLabel   || '';
        trayName.textContent  = card.dataset.name       || '';
        trayInput.value       = card.dataset.id         || '';
        if (trayPreviewLink) trayPreviewLink.href = card.dataset.previewUrl || '#';
        tray.classList.add('tpl-preview-tray--active');
        if (mainEl) mainEl.style.paddingBottom = '160px';
    }

    window.closeTray = function () {
        tray.classList.remove('tpl-preview-tray--active');
        if (mainEl) mainEl.style.paddingBottom = '';
        document.querySelectorAll('.tpl-card--selected').forEach(function (c) {
            c.classList.remove('tpl-card--selected');
        });
    };

    document.querySelectorAll('.tpl-card--selectable').forEach(function (card) {
        card.addEventListener('click', function () {
            document.querySelectorAll('.tpl-card').forEach(function (c) {
                c.classList.remove('tpl-card--selected');
            });
            card.classList.add('tpl-card--selected');
            openTray(card);
        });
    });

    document.querySelectorAll('.picker-tab').forEach(function (tab) {
        tab.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.picker-tab').forEach(function (t) {
                t.classList.remove('picker-tab--active');
            });
            this.classList.add('picker-tab--active');
            var filter = this.getAttribute('data-filter');
            document.querySelectorAll('.tpl-card').forEach(function (card) {
                card.style.display = (filter === 'all' || card.dataset.category === filter) ? '' : 'none';
            });
            var sel = document.querySelector('.tpl-card--selected');
            if (sel && sel.style.display === 'none') { window.closeTray(); }
        });
    });

    // Show filename next to file input
    document.querySelectorAll('.slot-file-input').forEach(function(input) {
        input.addEventListener('change', function() {
            var label = this.nextElementSibling ? this.nextElementSibling.nextElementSibling : null;
            if (label && this.files.length) {
                label.textContent = Array.from(this.files).map(function(f){ return f.name; }).join(', ');
            }
        });
    });
});
"""))

    return sidebar_layout(
        Div(content, _preview_tray(), picker_js),
        user=user,
        title="Okenaba — Choose Template",
        active_nav="pages",
    )
