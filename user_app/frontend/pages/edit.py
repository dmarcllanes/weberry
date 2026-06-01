"""Edit content page — lets users edit text or raw HTML on their generated site."""

from html.parser import HTMLParser

from fasthtml.common import (
    Div, H1, H2, P, Form, Button, Section, Iframe, A, Textarea, Label, Input, Span, Script, Safe,
)

from core.state_machine.states import ProjectState
from user_app.frontend.layout import page_layout


class TextExtractor(HTMLParser):
    """Extract editable text blocks from site HTML.

    Walks the HTML tree and pulls out text content from meaningful
    elements (headings, paragraphs, list items, etc.), skipping
    structural elements that users must not edit (nav, footer, style, script).
    """

    EDITABLE_TAGS = {
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "li", "a", "span", "td", "th", "blockquote", "label",
    }
    SKIP_PARENTS = {"style", "script", "nav", "footer"}

    def __init__(self):
        super().__init__()
        self.texts = []  # list of (tag, text) tuples
        self._stack = []
        self._skip_depth = 0
        self._current_tag = None
        self._current_text = ""

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        if tag in self.SKIP_PARENTS:
            self._skip_depth += 1
        if self._skip_depth == 0 and tag in self.EDITABLE_TAGS:
            self._current_tag = tag
            self._current_text = ""

    def handle_endtag(self, tag):
        if self._current_tag == tag and self._skip_depth == 0:
            text = self._current_text.strip()
            if text:
                self.texts.append((tag, text))
            self._current_tag = None
            self._current_text = ""
        if tag in self.SKIP_PARENTS and self._skip_depth > 0:
            self._skip_depth -= 1
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._skip_depth == 0 and self._current_tag is not None:
            self._current_text += data


def extract_editable_texts(html: str) -> list[tuple[str, str]]:
    """Return list of (tag, text) pairs from site HTML."""
    extractor = TextExtractor()
    extractor.feed(html)
    return extractor.texts


TAG_LABELS = {
    "h1": "Heading 1",
    "h2": "Heading 2",
    "h3": "Heading 3",
    "h4": "Heading 4",
    "h5": "Heading 5",
    "h6": "Heading 6",
    "p": "Paragraph",
    "li": "List Item",
    "a": "Link Text",
    "span": "Text",
    "td": "Table Cell",
    "th": "Table Header",
    "blockquote": "Quote",
    "label": "Label",
}


def edit_page(user, project, active_tab: str = "visual"):
    """Render the edit-content page for a project."""
    pid = project.id
    html_content = project.site_version.html if project.site_version else ""
    texts = extract_editable_texts(html_content)
    is_published = project.state == ProjectState.PUBLISHED

    # --- Published badge ---
    published_badge = (
        Span(
            Span(cls="edit-live-dot"),
            "Live",
            cls="edit-published-badge",
        )
        if is_published else ""
    )

    # --- Tab bar ---
    tab_bar = Div(
        A("Visual Editor", href=f"/pages/{pid}/edit?tab=visual",
          cls=f"edit-tab{'  edit-tab--active' if active_tab == 'visual' else ''}"),
        A("Text Fields", href=f"/pages/{pid}/edit?tab=text",
          cls=f"edit-tab{'  edit-tab--active' if active_tab == 'text' else ''}"),
        A("HTML Editor", href=f"/pages/{pid}/edit?tab=html",
          cls=f"edit-tab{'  edit-tab--active' if active_tab == 'html' else ''}"),
        cls="edit-tabs",
    )

    # --- Text editor panel ---
    fields = []
    for i, (tag, text) in enumerate(texts):
        label_text = TAG_LABELS.get(tag, tag.upper())
        rows = max(2, min(6, len(text) // 60 + 1))
        fields.append(
            Div(
                Label(label_text, cls="edit-label"),
                Input(type="hidden", name=f"original_{i}", value=text),
                Textarea(
                    text,
                    name=f"edited_{i}",
                    cls="input input-textarea edit-textarea",
                    rows=str(rows),
                    data_preview_text=text,
                ),
                cls="edit-field",
            )
        )

    if not fields:
        fields.append(P("No editable text found.", cls="step-description"))

    text_form = Form(
        *fields,
        Div(
            Button("Save Changes", cls="button button-primary", type="submit"),
            A("Cancel", href=f"/pages/{pid}", cls="button button-secondary"),
            cls="button-group",
        ),
        method="post",
        action=f"/pages/{pid}/edit-content",
        cls="form edit-form",
    )

    text_panel = Div(
        text_form,
        cls="edit-fields-panel",
        style="" if active_tab == "text" else "display:none",
    )

    # --- HTML editor panel ---
    html_form = Form(
        Div(
            Div(
                P(
                    "⚠️ You're editing raw HTML. "
                    "Changes go live immediately — invalid markup may break your page.",
                    cls="edit-html-hint",
                ),
                Textarea(
                    html_content,
                    name="html",
                    cls="edit-html-textarea",
                    rows="30",
                    spellcheck="false",
                    autocomplete="off",
                ),
                Div(
                    Button("Save HTML", cls="button button-primary", type="submit"),
                    A("Cancel", href=f"/pages/{pid}", cls="button button-secondary"),
                    Span(
                        "Changes update the preview and the live site.",
                        cls="edit-html-save-note",
                    ) if is_published else "",
                    cls="edit-html-actions",
                ),
                cls="edit-html-wrap",
            ),
            cls="edit-fields-panel",
        ),
        method="post",
        action=f"/pages/{pid}/edit-html",
        style="" if active_tab == "html" else "display:none",
    )

    # --- Visual editor panel (full-width iframe with inline editing) ---
    visual_panel = Div(
        Iframe(
            src=f"/pages/{pid}/preview-render?edit=1",
            cls="edit-visual-frame",
            title="Visual editor",
            id="visual-editor-frame",
        ),
        cls="edit-visual-panel",
        style="" if active_tab == "visual" else "display:none",
    )

    # Visual tab gets a full-width layout; text/html tabs keep the split layout
    if active_tab == "visual":
        editor_body = visual_panel
    else:
        editor_body = Div(
            Div(
                text_panel,
                html_form,
                cls="edit-fields-panel",
            ),
            Div(
                H2("Preview", cls="edit-preview-title"),
                Iframe(
                    src=f"/pages/{pid}/preview-render",
                    cls="site-preview-frame",
                    title="Site preview",
                ),
                cls="edit-preview-panel",
            ),
            cls="edit-page",
        )

    content = Div(
        Section(
            Div(
                Div(
                    H1("Edit Content", cls="step-title"),
                    published_badge,
                    cls="edit-page-header",
                ),
                P(
                    "Click any text on the page to edit it. Use Text Fields for bulk edits "
                    "or HTML Editor for full control.",
                    cls="step-description",
                ),
                tab_bar,
                editor_body,
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    preview_sync_js = Script(Safe("""
(function () {
  var frame = document.querySelector('.site-preview-frame');
  if (!frame) return;

  function injectStyle(doc) {
    if (doc.getElementById('__ob-hl-style__')) return;
    var s = doc.createElement('style');
    s.id = '__ob-hl-style__';
    s.textContent =
      '.__ob-hl{outline:2px solid #7c3aed!important;outline-offset:4px;border-radius:3px;' +
      'animation:ob-hl-pulse 1.4s ease-out;}' +
      '@keyframes ob-hl-pulse{0%{background:rgba(124,58,237,.25)}100%{background:transparent}}';
    doc.head.appendChild(s);
  }

  function scrollToText(text) {
    try {
      var doc = frame.contentDocument;
      if (!doc || !doc.body) return;
      injectStyle(doc);
      var prev = doc.querySelector('.__ob-hl');
      if (prev) prev.classList.remove('__ob-hl');
      var tags = 'h1,h2,h3,h4,h5,h6,p,li,button,td,th,blockquote,label,a,span';
      var els = doc.querySelectorAll(tags);
      for (var i = 0; i < els.length; i++) {
        if (els[i].innerText.trim() === text.trim()) {
          els[i].classList.add('__ob-hl');
          els[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }
      }
    } catch (e) {}
  }

  document.querySelectorAll('[data-preview-text]').forEach(function (el) {
    el.addEventListener('focus', function () {
      scrollToText(el.dataset.previewText);
    });
  });
})();
"""))

    save_modal = Div(
        Div(
            Div("✓", cls="ob-sm-icon"),
            H2("Changes Saved!", cls="ob-sm-title"),
            P("Your edits have been applied to your page.", cls="ob-sm-sub"),
            A("Go to Preview →", href=f"/pages/{pid}", cls="button button-primary ob-sm-btn"),
            P(
                Span("Redirecting in "),
                Span("3", id="ob-sm-countdown"),
                Span("s…"),
                cls="ob-sm-auto",
            ),
            cls="ob-sm-card",
        ),
        id="ob-save-modal", cls="ob-save-modal",
        style="display:none",
    )

    save_modal_css = Safe("""<style>
.ob-save-modal{
  position:fixed;inset:0;z-index:9999;
  background:rgba(7,7,15,.75);backdrop-filter:blur(6px);
  display:flex;align-items:center;justify-content:center;
}
.ob-sm-card{
  background:var(--color-surface,#0f0f24);
  border:1px solid rgba(124,58,237,.35);
  border-radius:1.25rem;
  padding:2.5rem 2.75rem;
  text-align:center;
  max-width:420px;width:90%;
  box-shadow:0 0 60px rgba(124,58,237,.25);
  animation:ob-sm-pop .25s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes ob-sm-pop{from{opacity:0;transform:scale(.88)}to{opacity:1;transform:scale(1)}}
.ob-sm-icon{
  width:64px;height:64px;
  background:linear-gradient(135deg,var(--color-primary,#2563eb),var(--color-primary-hover,#1d4ed8));
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:1.75rem;color:#fff;
  margin:0 auto 1.25rem;
  box-shadow:0 0 28px rgba(37,99,235,.4);
}
.ob-sm-title{font-size:1.5rem;font-weight:700;color:var(--color-text,#e2e8f0);margin:0 0 .5rem;}
.ob-sm-sub{color:#94a3b8;font-size:.95rem;margin:0 0 1.75rem;}
.ob-sm-btn{display:inline-block;padding:.75rem 2rem;font-size:1rem;border-radius:.75rem;}
.ob-sm-auto{margin-top:1.25rem;font-size:.85rem;color:#475569;}
</style>""")

    save_modal_js = Script(Safe(f"""
(function () {{
  function showSaveModal() {{
    var modal = document.getElementById('ob-save-modal');
    if (!modal) return;
    modal.style.display = 'flex';
    var countEl = document.getElementById('ob-sm-countdown');
    var secs = 3;
    var timer = setInterval(function () {{
      secs--;
      if (countEl) countEl.textContent = secs;
      if (secs <= 0) {{
        clearInterval(timer);
        window.location.href = '/pages/{pid}';
      }}
    }}, 1000);
  }}

  // Visual editor (iframe) signals save via postMessage
  window.addEventListener('message', function (e) {{
    if (e.data && e.data.type === 'ob-save-success') showSaveModal();
  }});

  // Intercept text-fields form submit
  document.addEventListener('DOMContentLoaded', function () {{
    var textForm = document.querySelector('form[action="/pages/{pid}/edit-content"]');
    if (textForm) {{
      textForm.addEventListener('submit', async function (e) {{
        e.preventDefault();
        var btn = textForm.querySelector('button[type="submit"]');
        if (btn) {{ btn.disabled = true; btn.textContent = 'Saving…'; }}
        try {{
          await fetch(textForm.action, {{
            method: 'POST',
            body: new FormData(textForm),
            redirect: 'follow',
          }});
          showSaveModal();
        }} catch (err) {{
          alert('Save failed. Please try again.');
          if (btn) {{ btn.disabled = false; btn.textContent = 'Save Changes'; }}
        }}
      }});
    }}

    // Intercept HTML editor form submit
    var htmlForm = document.querySelector('form[action="/pages/{pid}/edit-html"]');
    if (htmlForm) {{
      htmlForm.addEventListener('submit', async function (e) {{
        e.preventDefault();
        var btn = htmlForm.querySelector('button[type="submit"]');
        if (btn) {{ btn.disabled = true; btn.textContent = 'Saving…'; }}
        try {{
          await fetch(htmlForm.action, {{
            method: 'POST',
            body: new FormData(htmlForm),
            redirect: 'follow',
          }});
          showSaveModal();
        }} catch (err) {{
          alert('Save failed. Please try again.');
          if (btn) {{ btn.disabled = false; btn.textContent = 'Save HTML'; }}
        }}
      }});
    }}
  }});
}})();
"""))

    return page_layout(
        Div(content, preview_sync_js, save_modal_css, save_modal, save_modal_js),
        user=user, title="Okenaba - Edit Content", project_id=pid, active_nav="pages",
    )
