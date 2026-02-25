"""Login page with Google OAuth via Supabase JS SDK."""

from fasthtml.common import *
from fasthtml.svg import *
from fasthtml.common import Link # Explicit import if not in * or to be safe

from config.settings import SUPABASE_URL, SUPABASE_KEY, TURNSTILE_SITE_KEY


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
            Script(f"window.SUPABASE_URL='{SUPABASE_URL}';window.SUPABASE_KEY='{SUPABASE_KEY}';"),
            Script(src="https://challenges.cloudflare.com/turnstile/v0/api.js", async_=True, defer=True),
        ),
        Body(
            Div(
                # Icon
                Div(
                    Svg(
                        Path(d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"),
                        Polyline(points="10 17 15 12 10 7"),
                        Line(x1="15", y1="12", x2="3", y2="12"),
                        viewBox="0 0 24 24",
                        fill="none",
                        stroke="currentColor",
                        stroke_width="2",
                        stroke_linecap="round",
                        stroke_linejoin="round",
                    ),
                    cls="icon-container"
                ),
                
                H1("Welcome back"),
                P("Sign in to continue to your account", cls="subtitle"),
                
                # Turnstile widget — must be solved before Google button activates
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

                # Google Button (disabled until Turnstile passes)
                Button(
                    # Google Icon SVG
                    Svg(
                        Path(d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .533 5.333.533 12S5.867 24 12.48 24c3.44 0 6.013-1.133 8.053-3.24 2.08-2.16 2.72-5.187 2.72-7.76 0-.76-.067-1.467-.187-2.08H12.48z", fill="currentColor"),
                        viewBox="0 0 24 24",
                        style="width:20px;height:20px;"
                    ),
                    Span("Continue with Google"),
                    id="googleBtn",
                    cls="btn-google",
                    disabled=True,
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
