"""Login page with Google OAuth via Supabase JS SDK."""

from fasthtml.common import *
from fasthtml.svg import *
from fasthtml.common import Link # Explicit import if not in * or to be safe

from config.settings import SUPABASE_URL, SUPABASE_KEY


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
        ),
        Body(
            Div(
                # Logo
                Img(src="/static/img/logo.png", alt="Okenaba", cls="login-logo"),
                
                H1("Welcome back"),
                P("Sign in to continue to your account", cls="subtitle"),
                
                # Google Button
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
