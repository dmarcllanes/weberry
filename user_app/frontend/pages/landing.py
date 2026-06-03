from fasthtml.common import *
from fasthtml.svg import *

from config.settings import SUPABASE_URL, SUPABASE_KEY

# Planet star positions: (size_px, top%, left%, duration_s, delay_s, max_opacity)
_PLANET_STARS = [
    (1.5, 8,  12, 3.2, 0.5, 0.8),
    (1.0, 22, 83, 4.1, 1.2, 0.6),
    (2.0, 5,  62, 2.8, 0.8, 0.9),
    (1.5, 72, 7,  3.5, 0.3, 0.7),
    (1.0, 84, 88, 4.5, 1.5, 0.5),
    (2.0, 44, 97, 2.5, 0.1, 0.9),
    (1.0, 16, 46, 3.8, 0.6, 0.6),
    (1.5, 66, 30, 3.1, 1.0, 0.8),
    (1.0, 92, 54, 4.2, 0.7, 0.4),
    (2.0, 30, 3,  2.9, 0.2, 0.8),
    (1.5, 56, 72, 3.6, 1.3, 0.6),
    (1.0, 7,  91, 4.0, 0.9, 0.5),
    (1.5, 48, 18, 3.3, 0.4, 0.7),
    (1.0, 18, 38, 3.9, 1.1, 0.5),
]


def _planet_star(size, top, left, dur, delay, mo):
    return Div(
        cls="p-star",
        style=(
            f"width:{size}px;height:{size}px;"
            f"top:{top}%;left:{left}%;"
            f"--d:{dur}s;--dl:{delay}s;--mo:{mo}"
        ),
    )


def _hero_browser_mockup():
    return Div(
        Div(
            Div(
                Div(cls="hb-dot hb-dot-red"),
                Div(cls="hb-dot hb-dot-yel"),
                Div(cls="hb-dot hb-dot-grn"),
                cls="hb-dots",
            ),
            Div("okenaba.com/my-site", cls="hb-urlbar"),
            cls="hb-chrome",
        ),
        Div(Div(cls="hb-progress-fill"), cls="hb-progress"),
        Div(
            Div(cls="hb-nav-bar"),
            Div(
                Div(cls="hb-text-line hb-text-lg"),
                Div(cls="hb-text-line hb-text-md"),
                Div(cls="hb-cta-btn"),
                cls="hb-hero-section",
            ),
            Div(
                Div(cls="hb-card"),
                Div(cls="hb-card"),
                Div(cls="hb-card"),
                cls="hb-cards-row",
            ),
            cls="hb-body",
        ),
        Div(cls="hb-cursor"),
        cls="hero-browser-float",
    )


def _hero_stats_badge():
    return Div(
        Div(
            Div(cls="hsb-live-dot"),
            Span("LIVE", cls="hsb-live-text"),
            cls="hsb-live-row",
        ),
        Div(
            Span("60s", cls="hsb-num"),
            cls="hsb-metric",
        ),
        P("avg. time to go live", cls="hsb-label"),
        cls="hero-stats-badge",
    )


def _cosmic_planet():
    return Div(
        Div(cls="planet-glow"),
        Div(Div(cls="moon"), cls="orbit-path"),
        Div(
            Div(
                Img(src="/static/img/favicon.svg", alt="Okenaba", cls="planet-favicon"),
                Div(cls="planet-ring"),
                Div(cls="planet-ring ring-outer"),
                cls="planet-sphere",
            ),
            cls="planet-container",
        ),
        Div(*[_planet_star(*s) for s in _PLANET_STARS], cls="planet-stars"),
        _hero_browser_mockup(),
        _hero_stats_badge(),
        cls="hero-visual",
    )


def landing_page():
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0, viewport-fit=cover"),
            Meta(name="theme-color", content="#2563eb"),
            Meta(name="description", content="Describe your business and get a complete, professional website in under 60 seconds. No code, no designer, no waiting."),
            Meta(name="mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-capable", content="yes"),
            Meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
            Meta(name="apple-mobile-web-app-title", content="Okenaba"),
            Title("Okenaba — Launch Your Idea Into Orbit"),
            Link(rel="icon", type="image/svg+xml", href="/static/img/favicon.svg"),
            Link(rel="apple-touch-icon", href="/static/img/favicon.svg"),
            Link(rel="manifest", href="/static/manifest.json"),
            Link(rel="stylesheet", href="/static/css/landing.css?v=12"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap", rel="stylesheet"),
            Script(src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"),
            Script(f"window.SUPABASE_URL='{SUPABASE_URL}';window.SUPABASE_KEY='{SUPABASE_KEY}';"),
            Script(src="/static/js/auth_check.js"),
        ),
        Body(
            # ── Scroll progress bar ──
            Safe('<div id="scroll-progress"></div>'),
            # ── Cosmic background layers (fixed, z-index 0) ──
            Safe('<canvas id="cosmos-canvas"></canvas>'),
            Div(
                Div(cls="nebula-blob violet"),
                Div(cls="nebula-blob blue"),
                Div(cls="nebula-blob magenta"),
                Div(cls="nebula-blob teal"),
                cls="nebula-layer",
            ),

            # ── All foreground content ──
            Div(

                # Announcement banner
                Div(
                    # Fixed left badge
                    Div(
                        Span("⚡", cls="ab-badge-icon"),
                        Span("New", cls="ab-badge-text"),
                        cls="ab-badge",
                    ),
                    Div(cls="ab-divider"),
                    # Scrolling marquee
                    Div(
                        Div(
                            Span("🚀", cls="ab-item-icon"), Span("1 free credit on signup — no card required", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("⏱", cls="ab-item-icon"), Span("Go live in under 60 seconds", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("✨", cls="ab-item-icon"), Span("AI writes every word & designs the page", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("💳", cls="ab-item-icon"), Span("1 credit = 1 site. Buy only what you need", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("📱", cls="ab-item-icon"), Span("Mobile-ready. 100/100 PageSpeed. Always.", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            # duplicate for seamless loop
                            Span("🚀", cls="ab-item-icon"), Span("1 free credit on signup — no card required", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("⏱", cls="ab-item-icon"), Span("Go live in under 60 seconds", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("✨", cls="ab-item-icon"), Span("AI writes every word & designs the page", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("💳", cls="ab-item-icon"), Span("1 credit = 1 site. Buy only what you need", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            Span("📱", cls="ab-item-icon"), Span("Mobile-ready. 100/100 PageSpeed. Always.", cls="ab-item-text"),
                            Span("✦", cls="ab-sep"),
                            cls="ab-track",
                        ),
                        cls="ab-marquee",
                    ),
                    cls="announcement-banner",
                ),

                # Navbar
                Nav(
                    Div(
                        Div(
                            A(Img(src="/static/img/favicon.svg", alt="", cls="logo-icon"),
                              Span("kenaba", cls="logo-wordmark"),
                              href="/", cls="logo"),
                            Ul(
                                Li(A("Features",    href="#features")),
                                Li(A("How It Works", href="#how-it-works")),
                                Li(A("Pricing",     href="#pricing")),
                                Li(A("Contact",     href="#contact")),
                                cls="nav-links",
                            ),
                            Div(
                                A("Sign In", cls="btn-secondary", href="/login"),
                                Button(
                                    Span(cls="bar"), Span(cls="bar"), Span(cls="bar"),
                                    cls="mobile-menu-btn",
                                    onclick="toggleMobileMenu()",
                                ),
                                cls="nav-actions",
                            ),
                            cls="nav-content",
                        ),
                        Div(
                            Ul(
                                Li(A("Features",    href="#features",    onclick="toggleMobileMenu()")),
                                Li(A("How It Works", href="#how-it-works", onclick="toggleMobileMenu()")),
                                Li(A("Pricing",     href="#pricing",     onclick="toggleMobileMenu()")),
                                Li(A("Contact",     href="#contact",     onclick="toggleMobileMenu()")),
                                Li(A("Sign In",     href="/login",       cls="mobile-nav-cta")),
                                cls="mobile-nav-links",
                            ),
                            cls="mobile-menu", id="mobileMenu",
                        ),
                        cls="container",
                    ),
                    cls="navbar",
                ),

                # ── Hero ──────────────────────────────────────
                Header(
                    Div(
                        # Left: copy
                        Div(
                            Div(
                                Div(cls="eyebrow-dot"),
                                "Landing Page Builder for Non-Tech Founders",
                                cls="hero-eyebrow",
                            ),
                            H1(
                                "Your Professional Landing Page, ",
                                Span("Live in 60 Seconds", cls="gradient-word"),
                                cls="hero-title",
                            ),
                            P(
                                "Fill in your business name, industry, and brand color — "
                                "Okenaba's AI writes every word, picks the perfect design, "
                                "and publishes your landing page instantly. "
                                "No code. No WordPress. No hiring a dev.",
                                cls="hero-subtitle",
                            ),
                            Div(
                                A("Build My Page Free", cls="btn-primary", href="/login"),
                                A("See How It Works",   cls="btn-secondary", href="#how-it-works"),
                                cls="hero-buttons",
                            ),
                            P(
                                "✦ No credit card required  ·  1 free credit on signup",
                                cls="hero-meta",
                            ),
                            cls="hero-content",
                        ),
                        # Right: cosmic planet
                        _cosmic_planet(),
                        cls="container",
                    ),
                    cls="hero",
                ),

                # ── Social Proof ───────────────────────────────
                Section(
                    Div(
                        P("Trusted by next-gen founders and creators", cls="proof-label"),
                        Div(
                            Div(
                                Img(src="/static/img/brands/amazon.svg",      alt="Amazon",      cls="brand-logo"),
                                Img(src="/static/img/brands/facebook.svg",    alt="Facebook",    cls="brand-logo"),
                                Img(src="/static/img/brands/puma.svg",        alt="Puma",        cls="brand-logo"),
                                Img(src="/static/img/brands/lamborghini.svg", alt="Lamborghini", cls="brand-logo"),
                                Img(src="/static/img/brands/gucci.svg",       alt="Gucci",       cls="brand-logo"),
                                Img(src="/static/img/brands/pedigree.svg",    alt="Pedigree",    cls="brand-logo"),
                                Img(src="/static/img/brands/amazon.svg",      alt="Amazon",      cls="brand-logo"),
                                Img(src="/static/img/brands/facebook.svg",    alt="Facebook",    cls="brand-logo"),
                                Img(src="/static/img/brands/puma.svg",        alt="Puma",        cls="brand-logo"),
                                Img(src="/static/img/brands/lamborghini.svg", alt="Lamborghini", cls="brand-logo"),
                                Img(src="/static/img/brands/gucci.svg",       alt="Gucci",       cls="brand-logo"),
                                Img(src="/static/img/brands/pedigree.svg",    alt="Pedigree",    cls="brand-logo"),
                                cls="marquee-track",
                            ),
                            cls="brand-marquee",
                        ),
                        cls="container",
                    ),
                    cls="social-proof",
                ),

                # ── Pain vs Orbit ──────────────────────────────
                _pain_vs_orbit(),

                # ── Features ──────────────────────────────────
                Section(
                    Div(
                        P("Mission Control", cls="section-eyebrow"),
                        H2("Everything You Need to Reach Orbit"),
                        Div(
                            # Wide card — Speed
                            Div(
                                Div(
                                    Svg(Path(d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"),
                                        viewBox="0 0 24 24", fill="none", stroke="currentColor",
                                        stroke_width="2", stroke_linecap="round", stroke_linejoin="round"),
                                    cls="feature-icon-wrapper",
                                ),
                                H3("Blazing Fast Launch"),
                                P("Go from idea to live website in under 60 seconds. Our AI generates structure, copy, and images — instantly."),
                                cls="feature-card bento-wide",
                            ),
                            # Card — Design
                            Div(
                                Div(
                                    Svg(Path(d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"),
                                        viewBox="0 0 24 24", fill="none", stroke="currentColor",
                                        stroke_width="2", stroke_linecap="round", stroke_linejoin="round"),
                                    cls="feature-icon-wrapper",
                                ),
                                H3("Stellar Design"),
                                P("Premium, designer-quality layouts crafted for conversion."),
                                cls="feature-card",
                            ),
                            # Wide card — Mobile
                            Div(
                                Div(
                                    Svg(Rect(x="5", y="2", width="14", height="20", rx="2", ry="2"),
                                        Line(x1="12", y1="18", x2="12.01", y2="18"),
                                        viewBox="0 0 24 24", fill="none", stroke="currentColor",
                                        stroke_width="2", stroke_linecap="round", stroke_linejoin="round"),
                                    cls="feature-icon-wrapper",
                                ),
                                H3("Universal Signal"),
                                P("Pixel-perfect on every screen — desktop, tablet, and mobile. Your site reaches every orbit."),
                                cls="feature-card bento-wide",
                            ),
                            # Card — SEO
                            Div(
                                Div(
                                    Svg(Path(d="M23 6l-9.5 9.5-5-5L1 18"), Path(d="M17 6h6v6"),
                                        viewBox="0 0 24 24", fill="none", stroke="currentColor",
                                        stroke_width="2", stroke_linecap="round", stroke_linejoin="round"),
                                    cls="feature-icon-wrapper",
                                ),
                                H3("SEO Optimized"),
                                P("Built-in technical SEO so the universe can find you."),
                                cls="feature-card",
                            ),
                            cls="bento-grid",
                        ),
                        cls="container",
                    ),
                    id="features", cls="features",
                ),

                # ── How It Works ───────────────────────────────
                Section(
                    Div(
                        P("Launch Sequence", cls="section-eyebrow"),
                        H2("From Idea to Orbit in 4 Steps"),
                        Div(
                            Div(
                                Div("01", cls="step-number"),
                                H3("Pick a Template"),
                                P("Browse 6 industry categories and click the design that fits your brand. Takes 10 seconds — no account needed yet."),
                                cls="step",
                            ),
                            Div(
                                Div("02", cls="step-number"),
                                H3("Fill In Your Details"),
                                P("Business name, industry, description, and your brand color. That's it. No technical settings, no hosting config."),
                                cls="step",
                            ),
                            Div(
                                Div("03", cls="step-number"),
                                H3("AI Writes & Builds"),
                                P("Our AI reads your details, writes all your copy, selects images, and assembles your complete landing page in under 60 seconds."),
                                cls="step",
                            ),
                            Div(
                                Div("04", cls="step-number"),
                                H3("Publish & Share"),
                                P("Preview your page, edit any text if you'd like, then hit Publish. Your live URL is ready to share immediately."),
                                cls="step",
                            ),
                            cls="steps",
                        ),
                        cls="container",
                    ),
                    id="how-it-works", cls="how-it-works",
                ),

                # ── Template Showcase ─────────────────────────
                _showcase_section(),

                # ── Stats ──────────────────────────────────────
                Section(
                    Div(
                        Div(H4("98%"),  P("Launch Success Rate"), cls="stat-item"),
                        Div(H4("48h"),  P("Avg. Time to First Signal"), cls="stat-item"),
                        Div(H4("$2.3M"), P("Founder Capital Saved"), cls="stat-item"),
                        Div(H4("50+"),  P("Ideas Launched Into Orbit"), cls="stat-item"),
                        cls="container",
                    ),
                    cls="stats",
                ),

                # ── Zero Skills ───────────────────────────────
                _zero_skills_section(),

                # ── Pricing ────────────────────────────────────
                Section(
                    Div(
                        Div(
                            P("Choose Your Mission", cls="section-eyebrow"),
                            H2("Simple Pricing", cls="text-glow"),
                            P("Pay only for what you use. No subscriptions, no surprises.", cls="section-subtitle"),
                            Div(
                                Span("🎁 1 Free Credit on Signup — no card required", cls="badge-save"),
                                style="text-align:center",
                            ),
                            cls="pricing-header",
                        ),
                        Div(
                            # Starter
                            Div(
                                H3("Starter"),
                                Div(
                                    H4("$9", cls="price-amount"),
                                    Span(" one-time", cls="price-period"),
                                    cls="price-wrapper",
                                ),
                                P("Perfect for validating your first idea.", cls="plan-desc"),
                                Div(
                                    Span("5 credits", style="font-size:1.5rem;font-weight:800;color:#60a5fa"),
                                    Span(" · $1.80 / credit", style="font-size:0.85rem;color:#475569;margin-left:0.25rem"),
                                    style="margin-bottom:1.25rem",
                                ),
                                Ul(
                                    Li("✓ 5 AI-generated pages"),
                                    Li("✓ 30-day page lifetime each"),
                                    Li("✓ Custom brand colors & images"),
                                    Li("✓ Credits never expire"),
                                    cls="features-list",
                                ),
                                A("Get Started", cls="btn-secondary", href="/login"),
                                cls="pricing-card",
                            ),
                            # Growth (featured)
                            Div(
                                Span("Most Popular", cls="badge"),
                                H3("Growth"),
                                Div(
                                    H4("$19", cls="price-amount"),
                                    Span(" one-time", cls="price-period"),
                                    cls="price-wrapper",
                                ),
                                P("Best value for founders validating multiple ideas.", cls="plan-desc"),
                                Div(
                                    Span("15 credits", style="font-size:1.5rem;font-weight:800;color:#60a5fa"),
                                    Span(" · $1.27 / credit", style="font-size:0.85rem;color:#475569;margin-left:0.25rem"),
                                    style="margin-bottom:1.25rem",
                                ),
                                Ul(
                                    Li("✓ 15 AI-generated pages"),
                                    Li("✓ 30-day page lifetime each"),
                                    Li("✓ Custom brand colors & images"),
                                    Li("✓ Credits never expire"),
                                    Li("✓ Priority support"),
                                    cls="features-list",
                                ),
                                A("Buy Growth Pack", cls="btn-primary", href="/login"),
                                cls="pricing-card featured",
                            ),
                            # Studio
                            Div(
                                H3("Studio"),
                                Div(
                                    H4("$49", cls="price-amount"),
                                    Span(" one-time", cls="price-period"),
                                    cls="price-wrapper",
                                ),
                                P("For agencies and prolific builders who move fast.", cls="plan-desc"),
                                Div(
                                    Span("50 credits", style="font-size:1.5rem;font-weight:800;color:#60a5fa"),
                                    Span(" · $0.98 / credit", style="font-size:0.85rem;color:#475569;margin-left:0.25rem"),
                                    style="margin-bottom:1.25rem",
                                ),
                                Ul(
                                    Li("✓ 50 AI-generated pages"),
                                    Li("✓ 30-day page lifetime each"),
                                    Li("✓ Custom brand colors & images"),
                                    Li("✓ Credits never expire"),
                                    Li("✓ Priority support"),
                                    cls="features-list",
                                ),
                                A("Buy Studio Pack", cls="btn-secondary", href="/login"),
                                cls="pricing-card",
                            ),
                            cls="pricing-grid",
                        ),

                        # ── Enterprise / Full Product card ──────────────────
                        Div(
                            Div(
                                Span("✦ Ready to build something bigger?", cls="pricing-ent-eyebrow"),
                                Div(
                                    Div(
                                        H3("Your Complete App", cls="pricing-ent-title"),
                                        P(
                                            "Go beyond a marketing page. We build you a real, working product — "
                                            "where your customers can sign up, pay, book, and actually use your service. "
                                            "No technical knowledge needed on your end.",
                                            cls="pricing-ent-desc",
                                        ),
                                        Ul(
                                            Li(Span("✓", cls="ent-check"), Span("Customers can create accounts & log in")),
                                            Li(Span("✓", cls="ent-check"), Span("Accept payments directly in your app")),
                                            Li(Span("✓", cls="ent-check"), Span("Booking, ordering, or subscription system")),
                                            Li(Span("✓", cls="ent-check"), Span("Your own dashboard to manage everything")),
                                            Li(Span("✓", cls="ent-check"), Span("Works beautifully on phones & computers")),
                                            Li(Span("✓", cls="ent-check"), Span("Ongoing support — we stay with you")),
                                            cls="ent-features",
                                        ),
                                        cls="pricing-ent-left",
                                    ),
                                    Div(
                                        Span("Custom", cls="ent-price-label"),
                                        P("Scoped to your idea.", cls="ent-price-sub"),
                                        P("Tell us what you're building and we'll send you a clear breakdown — no jargon, no surprises.", cls="ent-price-note"),
                                        A("Let's Talk →", href="mailto:hello@okenaba.com", cls="btn-primary ent-cta"),
                                        cls="pricing-ent-right",
                                    ),
                                    cls="pricing-ent-inner",
                                ),
                                cls="pricing-ent-card",
                            ),
                            style="margin-top:2rem",
                        ),

                        Div(
                            Span("✦ ", style="font-size:1rem"),
                            Span(
                                "1 credit = 1 AI-generated page. Free signup credit lasts 7 days. "
                                "Purchased credits give each page a 30-day lifetime. Credits never expire.",
                                style="color:#475569;font-size:0.9rem",
                            ),
                            style="text-align:center;margin-top:2rem;padding:1rem 2rem;background:rgba(124,58,237,0.06);border-radius:0.75rem;border:1px solid rgba(124,58,237,0.12)",
                        ),
                        cls="container",
                    ),
                    id="pricing", cls="pricing",
                ),

                # ── Comparison ────────────────────────────────
                _comparison_section(),

                # ── Business Survey ────────────────────────────
                Section(
                    # Ambient orbs
                    Div(cls="survey-orb survey-orb--left"),
                    Div(cls="survey-orb survey-orb--right"),
                    # Orbit rings
                    Div(cls="survey-ring survey-ring--1"),
                    Div(cls="survey-ring survey-ring--2"),
                    Div(cls="survey-ring survey-ring--3"),
                    Div(
                        # Header
                        Div(
                            Div(
                                Span("✦", cls="survey-eyebrow-star"),
                                Span("Shape The Future", cls="survey-eyebrow-text"),
                                Span("✦", cls="survey-eyebrow-star"),
                                cls="survey-eyebrow",
                            ),
                            H2(
                                Span("Tell Us About", cls="survey-title-plain"),
                                Span(" Your Mission", cls="survey-title-glow"),
                                cls="survey-heading",
                            ),
                            P(
                                "Help us tailor Okenaba to your vision. "
                                "Every answer shapes better templates for founders like you.",
                                cls="survey-subtitle",
                            ),
                            cls="survey-header",
                        ),
                        # Card
                        Div(
                            # Decorative top bar
                            Div(cls="survey-card-bar"),
                            # Floating badge
                            Div("🚀 Founders Only", cls="survey-badge"),
                            Form(
                                # Business Name
                                Div(
                                    Label(
                                        Span("⬡", cls="survey-field-icon"),
                                        Span("Business Name"),
                                        cls="survey-label",
                                    ),
                                    Div(
                                        Input(type="text", name="business_name",
                                              placeholder="e.g. Nebula Corp",
                                              cls="survey-input"),
                                        cls="survey-input-wrap",
                                    ),
                                    cls="survey-group",
                                ),
                                # Industry
                                Div(
                                    Label(
                                        Span("◈", cls="survey-field-icon"),
                                        Span("Industry"),
                                        cls="survey-label",
                                    ),
                                    Div(
                                        Select(
                                            Option("Select your orbit...", value="", disabled=True, selected=True),
                                            Option("Technology & SaaS",       value="tech"),
                                            Option("E-commerce & Retail",     value="ecommerce"),
                                            Option("Professional Services",   value="services"),
                                            Option("Creative & Design",       value="creative"),
                                            Option("Health & Wellness",       value="health"),
                                            Option("Other",                   value="other"),
                                            name="industry", cls="survey-select",
                                        ),
                                        cls="survey-input-wrap survey-select-wrap",
                                    ),
                                    cls="survey-group",
                                ),
                                # Description
                                Div(
                                    Label(
                                        Span("◎", cls="survey-field-icon"),
                                        Span("Your Mission"),
                                        cls="survey-label",
                                    ),
                                    Div(
                                        Textarea(
                                            name="description",
                                            placeholder="Briefly describe your idea — what problem are you solving?",
                                            cls="survey-textarea", rows="4",
                                        ),
                                        cls="survey-input-wrap",
                                    ),
                                    cls="survey-group",
                                ),
                                # Submit
                                Div(
                                    Button(
                                        Span("Transmit Your Mission", cls="survey-btn-label"),
                                        Span("→", cls="survey-btn-arrow"),
                                        cls="survey-submit",
                                    ),
                                    P("Your signal shapes the universe. No spam, ever.", cls="survey-privacy"),
                                    cls="survey-footer",
                                ),
                                cls="survey-form-inner",
                                onsubmit="surveySubmit(event)",
                            ),
                            cls="survey-card",
                        ),
                        cls="survey-wrap container",
                    ),
                    id="business-survey", cls="survey-section",
                ),

                # ── Testimonials ───────────────────────────────
                Section(
                    Div(
                        P("Signals From The Field", cls="section-eyebrow"),
                        H2("What Creators Say"),
                        Div(
                            _testimonial(
                                '"Okenaba helped me validate my SaaS concept before building. I saved 6 months and $50k!"',
                                "Sarah Chen", "Founder, TechFlow",
                                "SC", "linear-gradient(135deg, #FF6B6B, #EE5D5D)",
                            ),
                            _testimonial(
                                '"The community feedback was invaluable. I pivoted my product and it\'s now 3× more successful."',
                                "Marcus Johnson", "Entrepreneur",
                                "MJ", "linear-gradient(135deg, #4ECDC4, #45B7AF)",
                            ),
                            _testimonial(
                                '"Built my online identity from zero to a recognized brand in 3 months. Highly recommend!"',
                                "Alex Rivera", "Creator",
                                "AR", "linear-gradient(135deg, #3b82f6, #1d4ed8)",
                            ),
                            cls="testimonials-grid",
                        ),
                        cls="container",
                    ),
                    cls="testimonials",
                ),

                # ── FAQ ───────────────────────────────────────
                _faq_section(),

                # ── CTA ────────────────────────────────────────
                Section(
                    Div(
                        H2("Your Landing Page Is 60 Seconds Away"),
                        P("No WordPress. No developer. No AI prompting. Just fill in your business details, pick a color, and go live — it really is that simple."),
                        A("Build My Page Free", cls="btn-primary", href="/login"),
                        cls="container cta-content",
                    ),
                    id="cta", cls="cta",
                ),

                # ── Footer ─────────────────────────────────────
                Footer(
                    Div(
                        Div(
                            Div(
                                A(Img(src="/static/img/favicon.svg", alt="", cls="logo-icon"),
                                  Span("kenaba", cls="logo-wordmark"),
                                  href="/", cls="logo"),
                                P("Professional landing pages for non-tech founders. Fill in your details, pick a color, go live in 60 seconds.",
                                  style="margin-top:1.5rem;color:#475569;font-size:0.9rem"),
                                cls="footer-section",
                            ),
                            Div(H4("Product"),
                                Ul(Li(A("Features", href="#features")), Li(A("Pricing", href="#pricing")), Li(A("Blog", href="#"))),
                                cls="footer-section"),
                            Div(H4("Company"),
                                Ul(Li(A("About", href="#")), Li(A("Careers", href="#")), Li(A("Contact", href="#"))),
                                cls="footer-section"),
                            Div(H4("Legal"),
                                Ul(Li(A("Privacy", href="#")), Li(A("Terms", href="#")), Li(A("Security", href="#"))),
                                cls="footer-section"),
                            cls="footer-content",
                        ),
                        Div(
                            P("© 2025 Okenaba. All rights reserved."),
                            Div(
                                A(Img(src="/static/img/brands/twitter.svg",  alt="Twitter"),  href="#"),
                                A(Img(src="/static/img/brands/linkedin.svg", alt="LinkedIn"), href="#"),
                                A(Img(src="/static/img/brands/discord.svg",  alt="Discord"),  href="#"),
                                cls="social-links",
                            ),
                            cls="footer-bottom",
                        ),
                        cls="container",
                    ),
                    cls="footer",
                ),

                # Cookie Banner
                Div(
                    Div(
                        Div(
                            Div(
                                Svg(Path(d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z",
                                        fill="currentColor"),
                                    viewBox="0 0 24 24", cls="cookie-icon"),
                                Div(
                                    P("We use cookies", cls="cookie-title"),
                                    P("We use cookies to enhance your browsing experience and analyze traffic.",
                                      cls="cookie-desc"),
                                    cls="cookie-text",
                                ),
                                cls="cookie-info",
                            ),
                            Div(
                                Button("Decline",    cls="btn-secondary cookie-btn", id="cookie-decline"),
                                Button("Accept All", cls="btn-primary cookie-btn",  id="cookie-accept"),
                                cls="cookie-actions",
                            ),
                            cls="cookie-inner",
                        ),
                        cls="container",
                    ),
                    id="cookie-banner", cls="cookie-banner",
                ),

                cls="cosmos-content",
            ),

            Script(src="/static/js/landing.js"),
        ),
        lang="en",
    )


def _pain_vs_orbit():
    def pain_item(emoji, title, desc):
        return Div(
            Div(emoji, cls="pvo-item-icon-wrap"),
            Div(P(title, cls="pvo-item-title"), P(desc, cls="pvo-item-desc")),
            cls="pvo-item pvo-item--pain",
        )

    def orbit_item(emoji, title, desc):
        return Div(
            Div(emoji, cls="pvo-item-icon-wrap"),
            Div(P(title, cls="pvo-item-title"), P(desc, cls="pvo-item-desc")),
            cls="pvo-item pvo-item--orbit",
        )

    return Section(
        Div(
            P("There Is A Better Way", cls="section-eyebrow"),
            H2("Skip WordPress. Skip the Dev. Go Live in 60 Seconds."),
            P(
                "Non-tech founders waste weeks and thousands trying to get a basic landing page up. "
                "WordPress is too complex. AI dev tools need coding knowledge. Freelancers take forever. "
                "Okenaba was built to solve exactly this.",
                cls="section-subtitle",
            ),
            Div(
                Div(
                    Div(Span("😤", cls="pvo-card-emoji"), H3("The Hard Way", cls="pvo-card-title pvo-card-title--pain"), cls="pvo-card-header"),
                    pain_item("🔧", "Set up WordPress", "Install plugins, pick a theme, configure hosting. Days of setup and it still looks generic."),
                    pain_item("💻", "Use Lovable or Claude Code", "AI tools built for developers. You still need to prompt, review code, and redeploy. Not for non-tech founders."),
                    pain_item("💸", "Hire a freelancer", "Pay $3,000–$10,000. Wait 4–8 weeks. Every revision costs more."),
                    cls="pvo-card pvo-card--pain",
                ),
                Div(Div("→", cls="pvo-arrow-icon"), cls="pvo-divider"),
                Div(
                    Div(Span("🚀", cls="pvo-card-emoji"), H3("The Okenaba Way", cls="pvo-card-title pvo-card-title--orbit"), cls="pvo-card-header"),
                    orbit_item("✍️", "Fill in your details", "Business name, industry, contact info — and pick your brand color. 30 seconds. Plain English, no jargon."),
                    orbit_item("🤖", "AI builds your page", "Picks the best template, writes all your copy, drops in images — full landing page in under 60 seconds."),
                    orbit_item("🌐", "You're live", "One click to publish. Share your URL. Done before your coffee gets cold."),
                    cls="pvo-card pvo-card--orbit",
                ),
                cls="pvo-grid",
            ),
            cls="container",
        ),
        cls="pain-vs-orbit",
    )


def _showcase_section():
    from core.raw_template.loader import get_template_srcdoc

    _CARDS = [
        ("technology/technology_four",  "Tech & SaaS",        "Modern SaaS Landing",  "Clean feature grids, trust signals, and CTAs that convert visitors into users."),
        ("food/food_five",              "Food & Restaurant",   "Culinary Delight",      "Mouthwatering layouts with menus, gallery sections, and reservation flows."),
        ("travel/travel_eight",         "Travel & Tours",      "Wanderlust",            "Vibrant, adventure-focused pages that inspire clicks and bookings instantly."),
        ("portfolio/portfolio_eight",   "Creative & Agency",   "Portfolio Showcase",    "Bold, expressive layouts for creatives, studios, and personal brands."),
        ("ecom/ecom_eight",             "E-Commerce",          "Product Launch",        "Sell with urgency — social proof, pricing, and a focused call-to-action."),
        ("onlinebiz/onlinebiz_five",    "Online Business",     "Authority Builder",     "Position yourself as the go-to expert in your niche. Credibility, instantly."),
    ]

    def sc_card(tpl_id, category, title, desc):
        return Div(
            Div(
                Div(
                    Iframe(
                        srcdoc=get_template_srcdoc(tpl_id),
                        cls="sc-card-iframe",
                        tabindex="-1",
                        scrolling="no",
                        sandbox="allow-same-origin",
                    ),
                    cls="sc-iframe-wrap",
                ),
                cls="sc-card-thumb",
            ),
            Div(
                Span(category, cls="sc-card-cat"),
                P(title, cls="sc-card-title"),
                P(desc, cls="sc-card-desc"),
                cls="sc-card-body",
            ),
            cls="sc-card",
        )

    scale_js = Script(Safe("""
(function () {
    function scaleWrap(wrap) {
        var iframe = wrap.querySelector('.sc-card-iframe');
        if (!iframe) return;
        var scale = wrap.offsetWidth / 1280;
        iframe.style.width           = '1280px';
        iframe.style.height          = Math.ceil(wrap.offsetHeight / scale) + 'px';
        iframe.style.transform       = 'scale(' + scale + ')';
        iframe.style.transformOrigin = 'top left';
    }
    function scaleAll() {
        document.querySelectorAll('.sc-iframe-wrap').forEach(scaleWrap);
    }
    document.addEventListener('DOMContentLoaded', scaleAll);
    window.addEventListener('resize', scaleAll);
    document.querySelectorAll('.sc-card-iframe').forEach(function (f) {
        f.addEventListener('load', function () { scaleWrap(f.parentElement); });
    });
})();
"""))

    return Section(
        Div(
            Div(
                Div(
                    P("Template Universe", cls="section-eyebrow"),
                    H2("Your Future Site Lives Here"),
                    P("AI picks the perfect template for your industry. Every one is mobile-perfect, fast, and built to convert.", cls="section-subtitle"),
                ),
                A("Browse All →", href="/login", cls="btn-secondary", style="white-space:nowrap;align-self:flex-end"),
                cls="showcase-intro",
            ),
            Div(
                *[sc_card(*c) for c in _CARDS],
                cls="sc-strip",
            ),
            scale_js,
            cls="container",
        ),
        cls="showcase",
    )


def _zero_skills_section():
    def zs_step(num, title, timing, desc):
        return Div(
            Div(Div(num, cls="zs-step-num"), Div(cls="zs-step-line"), cls="zs-step-left"),
            Div(
                P(timing, cls="zs-step-sub"),
                P(title, cls="zs-step-title"),
                P(desc, cls="zs-step-desc"),
                cls="zs-step-body",
            ),
            cls="zs-step",
        )

    return Section(
        Div(
            Div(
                Div(
                    P("Built for Non-Tech Founders", cls="section-eyebrow"),
                    H2("If You Can Type, You Can Build", cls="zs-left-heading"),
                    P(
                        "No WordPress plugins. No AI prompting. No developer. "
                        "Just fill in what your business does and pick a color — "
                        "Okenaba handles the rest.",
                        cls="zs-left-sub",
                    ),
                    Div(
                        Span("✓ No coding", cls="zs-badge"),
                        Span("✓ No WordPress setup", cls="zs-badge"),
                        Span("✓ No design skills needed", cls="zs-badge"),
                        Span("✓ No hosting config", cls="zs-badge"),
                        cls="zs-badge-row",
                    ),
                    cls="zs-left",
                ),
                Div(
                    zs_step("1", "Fill In Your Business Details", "Step 1 — 30 seconds",
                             "Business name, industry, what you offer, and your brand color. That's all we need. No technical setup, no confusing options."),
                    zs_step("2", "AI Designs & Writes Everything", "Step 2 — under 60 seconds",
                             "Okenaba picks the best template for your industry, writes tailored copy for your page, and assembles the full landing page automatically."),
                    zs_step("3", "You're Live", "Step 3 — instantly",
                             "Review your page, edit any text if you like, then click Publish. Your live link is ready to share — no hosting setup, no domain config."),
                    cls="zs-steps",
                ),
                cls="zero-skills-inner",
            ),
            cls="container",
        ),
        cls="zero-skills",
    )


def _comparison_section():
    # (val, kind) — kind: "good" | "bad" | "meh" | "ok"
    ROWS = [
        ("⏱ Time to live",       [("3–7 days setup",             "bad"),  ("1–3 days of prompting",  "bad"),  ("4–8 weeks",             "bad"),  ("3–7 days learning",    "bad"),  ("Under 60 seconds",        "good")]),
        ("💰 Real cost",          [("$10–$40/mo + plugins",       "bad"),  ("$20–$50 / month",        "bad"),  ("$3,000–$10,000",        "bad"),  ("$15–$40 / month",      "meh"),  ("Free → $9 one-time",      "good")]),
        ("🧠 Tech skill needed",  [("Hosting, themes, plugins",   "bad"),  ("Prompting + code review","meh"),  ("None, lots of meetings","meh"),  ("Drag-drop learning",   "meh"),  ("Zero — plain English",    "good")]),
        ("🎨 Design quality",     [("Generic, theme-locked",      "meh"),  ("Inconsistent output",    "meh"),  ("Depends on freelancer", "meh"),  ("Generic templates",    "bad"),  ("Pro-grade, AI-optimized", "good")]),
        ("🔄 Consistent output",  [("Varies by plugin/theme",     "meh"),  ("Varies every session",   "bad"),  ("Depends on person",     "meh"),  ("Template-locked",      "meh"),  ("Same quality every time", "good")]),
        ("👤 Non-tech founder",   [("Partial — overwhelming",     "meh"),  ("No — built for builders","bad"),  ("Yes — expensive",       "meh"),  ("Partial — needs time",  "meh"),  ("Yes — built for you",     "good")]),
        ("🔧 After-launch edits", [("Plugins & dashboard",        "meh"),  ("Re-prompt, re-deploy",   "bad"),  ("Back-and-forth + cost", "bad"),  ("Manual, hours/change",  "bad"),  ("Click & type, instant",   "good")]),
        ("📦 Hosting included",   [("No — extra cost",            "bad"),  ("No",                     "bad"),  ("Extra cost",            "bad"),  ("Yes (subscription)",   "meh"),  ("Yes, always",             "good")]),
    ]

    COLS = [
        ("🔧", "WordPress",          "Install, configure plugins, manage hosting. Not built for non-tech users."),
        ("💻", "Lovable / Claude Code", "AI coding tools built for developers — requires prompting, code review, and redeployment."),
        ("🧑‍💻", "Hire a Freelancer",  "Traditional route. Expensive, slow, lots of back-and-forth."),
        ("🛠️", "Wix / Squarespace",  "Drag-and-drop builders. Hours of learning for average results."),
        ("🚀", "Okenaba",            "Fill in your details, pick a color. AI builds your landing page. Done."),
    ]

    def cell(val, kind):
        icons = {"good": "✓", "bad": "✗", "meh": "~", "ok": "~"}
        return Td(
            Span(icons.get(kind, ""), cls=f"ct-icon ct-icon--{kind}"),
            Span(val, cls="ct-val"),
            cls=f"ct-cell ct-cell--{kind}",
        )

    header_cells = []
    for i, (icon, name, _) in enumerate(COLS):
        is_hero = (i == len(COLS) - 1)
        header_cells.append(
            Th(
                Span(icon, cls="ct-col-icon"),
                Div(name, cls="ct-col-name"),
                Span("Best pick", cls="ct-hero-badge") if is_hero else "",
                cls="ct-col-hero" if is_hero else "ct-col",
            )
        )

    body_rows = []
    for label, values in ROWS:
        row_cells = [Td(label, cls="ct-row-label")]
        for i, (val, kind) in enumerate(values):
            is_hero = (i == len(values) - 1)
            td = cell(val, kind)
            if is_hero:
                td.attrs["class"] = td.attrs.get("class", "") + " ct-cell--hero-col"
            row_cells.append(td)
        body_rows.append(Tr(*row_cells, cls="ct-row"))

    tagline_row = [Td("")]
    for i, (_, _, tagline) in enumerate(COLS):
        is_hero = (i == len(COLS) - 1)
        tagline_row.append(
            Td(tagline, cls="ct-tagline ct-tagline--hero" if is_hero else "ct-tagline")
        )

    return Section(
        Div(
            Div(
                P("Do The Math", cls="section-eyebrow"),
                H2("Why Okenaba Wins Every Time"),
                P(
                    "WordPress needs plugins and a hosting setup. Lovable and Claude Code are built for developers. "
                    "Freelancers take weeks and thousands. Okenaba gives non-tech founders a professional landing page in 60 seconds — at a fraction of the cost.",
                    cls="section-subtitle",
                ),
                cls="comp-intro",
            ),
            Div(
                Div(
                    Table(
                        Thead(Tr(Th("", cls="ct-row-label"), *header_cells)),
                        Tbody(
                            Tr(*tagline_row, cls="ct-tagline-row"),
                            *body_rows,
                        ),
                        cls="comp-table",
                    ),
                    cls="comp-table-scroll",
                ),
                cls="comp-table-wrap",
            ),
            cls="container",
        ),
        cls="comparison",
    )


def _faq_section():
    faqs = [
        ("Do I need any technical skills?",
         "Zero. If you can fill out a form and pick a color, you can build with Okenaba. We handle the code, design, hosting, and everything else behind the scenes — no WordPress, no prompting AI tools, no developer required."),
        ("How is this different from WordPress or Wix?",
         "WordPress and Wix require you to install themes, configure plugins, manage hosting, and spend hours learning the interface. With Okenaba, you fill in your business details once, and AI generates your professional landing page in under 60 seconds. No setup, no learning curve."),
        ("How is this different from Lovable or Claude Code?",
         "Lovable and Claude Code are AI tools built for developers and technically-savvy builders — you still need to write prompts, review generated code, and redeploy. Okenaba is built specifically for non-tech founders. You describe your business; we handle everything else."),
        ("How fast can I really go live?",
         "Most users are live in under 2 minutes. The AI generation takes about 60 seconds. The rest is just reviewing your page and clicking Publish."),
        ("What if I don't like the generated page?",
         "You can edit any text directly on the page, swap images, or change your brand color. There's also a raw HTML editor if you want full control. Your page, your rules."),
        ("Do I need to pay for hosting?",
         "No. Your page is hosted by Okenaba automatically. One credit = one landing page, hosted for 30 days. Purchased credits never expire — use them whenever you're ready."),
    ]

    items = [
        Details(
            Summary(Span(q, cls="faq-q-text"), Span("+", cls="faq-toggle"), cls="faq-question"),
            Div(P(a), cls="faq-answer"),
            cls="faq-item",
        )
        for q, a in faqs
    ]

    return Section(
        Div(
            P("Mission Briefing", cls="section-eyebrow"),
            H2("Questions Before Launch?"),
            P("Everything you need to know before you hit that Publish button.", cls="section-subtitle faq-section"),
            Div(*items, cls="faq-list"),
            cls="container",
        ),
        cls="faq-section",
    )


def _star_svg():
    return Svg(
        Path(d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"),
        viewBox="0 0 24 24", fill="#fbbf24", stroke="none", cls="icon-star",
    )


def _testimonial(quote, name, role, initials, gradient):
    return Div(
        Div(*[_star_svg() for _ in range(5)], cls="stars"),
        P(quote, cls="testimonial-text"),
        Div(
            Div(initials, cls="avatar-placeholder", style=f"background:{gradient}"),
            Div(P(name, cls="author-name"), P(role, cls="author-role"), cls="author-info"),
            cls="testimonial-author",
        ),
        cls="testimonial-card",
    )
