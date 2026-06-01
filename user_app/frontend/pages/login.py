"""Login page with Google OAuth via Supabase JS SDK."""

from fasthtml.common import *
from fasthtml.common import Link

import os
from config.settings import SUPABASE_URL, SUPABASE_KEY, TURNSTILE_SITE_KEY

_TURNSTILE_DISABLED = os.environ.get("TURNSTILE_DISABLED", "false").lower() == "true"


def login_page():
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Login — Okenaba"),
            Link(rel='icon', type='image/svg+xml', href='/static/img/favicon.svg'),
            Link(rel="stylesheet", href="/static/css/login-glass.css"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap", rel="stylesheet"),
            Script(src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"),
            Script(f"window.SUPABASE_URL='{SUPABASE_URL}';window.SUPABASE_KEY='{SUPABASE_KEY}';window.TURNSTILE_DISABLED={str(_TURNSTILE_DISABLED).lower()};"),
            *([Script(src="https://challenges.cloudflare.com/turnstile/v0/api.js", async_=True, defer=True)]
              if not _TURNSTILE_DISABLED else []),
        ),
        Body(
            Div(cls="nebula-blob violet"),
            Div(cls="nebula-blob blue"),
            Div(cls="nebula-blob magenta"),
            Div(
                Div(
                    Img(src="/static/img/favicon.svg", alt="", cls="login-logo-icon"),
                    Span("kenaba", cls="login-logo-wordmark"),
                    cls="login-logo",
                ),

                H1("Welcome back"),
                P("Sign in to continue to your account", cls="subtitle"),
                
                # Turnstile widget (hidden when disabled)
                *([] if _TURNSTILE_DISABLED else [
                    Div(
                        Div(
                            data_sitekey=TURNSTILE_SITE_KEY,
                            data_callback="onTurnstileSuccess",
                            data_expired_callback="onTurnstileExpired",
                            data_theme="dark",
                            cls="cf-turnstile",
                        ),
                        cls="turnstile-container",
                    ),
                ]),

                # Google Button (always enabled when Turnstile disabled, else waits for it)
                Button(
                    Svg(
                        Path(d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .533 5.333.533 12S5.867 24 12.48 24c3.44 0 6.013-1.133 8.053-3.24 2.08-2.16 2.72-5.187 2.72-7.76 0-.76-.067-1.467-.187-2.08H12.48z", fill="currentColor"),
                        viewBox="0 0 24 24",
                        style="width:20px;height:20px;"
                    ),
                    Span("Continue with Google"),
                    id="googleBtn",
                    cls="btn-google",
                    disabled=(not _TURNSTILE_DISABLED),
                ),

                Div(
                    Span("OR"),
                    cls="divider"
                ),

                Div(
                    A("Back", href="/", cls="btn-back"),
                    cls="create-account"
                ),

                Div(
                    "By continuing, you agree to our ",
                    A("Terms", href="#"),
                    " & ",
                    A("Privacy Policy", href="#"),
                    cls="footer-links"
                ),

                cls="login-card",
            ),
            Script(src="/static/js/login.js"),
        ),
    )
