"""Edit content page — lets users edit text on their generated site."""

from html.parser import HTMLParser

from fasthtml.common import (
    Div, H1, H2, P, Form, Button, Section, Iframe, A, Textarea, Label, Input,
)

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


def edit_page(user, project):
    """Render the edit-content page for a project."""
    pid = project.id
    html = project.site_version.html if project.site_version else ""
    texts = extract_editable_texts(html)

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
                ),
                cls="edit-field",
            )
        )

    if not fields:
        fields.append(P("No editable text found.", cls="step-description"))

    form = Form(
        *fields,
        Div(
            Button("Save Changes", cls="button button-primary", type="submit"),
            A("Cancel", href=f"/projects/{pid}", cls="button button-secondary"),
            cls="button-group",
        ),
        method="post",
        action=f"/projects/{pid}/edit-content",
        cls="form edit-form",
    )

    content = Div(
        Section(
            Div(
                H1("Edit Content", cls="step-title"),
                P(
                    "Edit the text on your website. You can fix typos and change wording. "
                    "Navigation and footer content are locked.",
                    cls="step-description",
                ),
                Div(
                    Div(
                        form,
                        cls="edit-fields-panel",
                    ),
                    Div(
                        H2("Preview", cls="edit-preview-title"),
                        Iframe(
                            src=f"/projects/{pid}/preview-render",
                            cls="site-preview-frame",
                            title="Site preview",
                        ),
                        cls="edit-preview-panel",
                    ),
                    cls="edit-page",
                ),
                cls="step-content",
            ),
            cls="step",
        ),
        cls="project-page",
    )

    return page_layout(content, user=user, title="Okenaba - Edit Content", project_id=pid, active_nav="projects")
