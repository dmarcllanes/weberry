import json

from fasthtml.common import Response

from user_app.frontend.layout import page_layout, error_banner

from fasthtml.common import Div, H1, P, A, Section


def json_error(message: str, status_code: int = 400) -> Response:
    return Response(
        json.dumps({"error": message}),
        media_type="application/json",
        status_code=status_code,
    )


def error_page(message: str, status_code: int = 400):
    """Return an HTML error page."""
    content = Section(
        Div(
            Div("\u26a0\ufe0f", cls="error-icon"),
            H1("Something went wrong", cls="step-title"),
            P(message, cls="step-description"),
            A("Back to Dashboard", href="/", cls="button button-primary",
              style="margin-top:2rem;max-width:300px;display:inline-block"),
            cls="step-content error-page-content",
        ),
        cls="step",
    )
    return page_layout(content, title="Okenaba - Error")
