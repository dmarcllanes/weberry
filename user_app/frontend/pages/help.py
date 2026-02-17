"""Help page — Guides, FAQ, and Support."""

from fasthtml.common import Div, H1, H2, H3, P, A, Section, Ul, Li, Button, Form, Input, Textarea
from user_app.frontend.layout import page_layout


def help_page(user):
    """Render the help center."""
    
    # Hero Section
    hero = Section(
        H1("How can we help you?", style="font-size:2.5rem;margin-bottom:1rem;text-align:center"),
        P("Find answers, read guides, or get in touch.", style="text-align:center;color:var(--color-text-light);font-size:1.2rem"),
        cls="help-hero",
        style="padding:3rem 0;margin-bottom:2rem"
    )

    # Guides Section
    guides = Div(
        H2("Guides & Tutorials", style="margin-bottom:1.5rem;border-bottom:1px solid var(--color-border);padding-bottom:0.5rem"),
        Div(
            _guide_card("Getting Started", "Learn the basics of Okenaba and how to set up your account.", "#"),
            _guide_card("Creating Your First Site", "Step-by-step walkthrough of the site generation process.", "#"),
            _guide_card("Editing Content", "How to use the editor to customize your website text and images.", "#"),
            _guide_card("Publishing & Domains", "Go live with your site and connect custom domains.", "#"),
            cls="guide-grid",
            style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1.5rem;margin-bottom:3rem"
        )
    )

    # FAQ Section
    faq = Div(
        H2("Frequently Asked Questions", style="margin-bottom:1.5rem;border-bottom:1px solid var(--color-border);padding-bottom:0.5rem"),
        Div(
            _faq_item("Is Okenaba free to use?", "Okenaba offers a free trial so you can explore all features. After that, you can choose a plan that suits your needs."),
            _faq_item("Can I use my own domain?", "Yes! You can connect any custom domain you own to your published Okenaba site."),
            _faq_item("How do I cancel my subscription?", "You can manage your subscription settings directly from the Billing page in your account menu."),
            cls="faq-list",
            style="display:flex;flex-direction:column;gap:1rem;margin-bottom:3rem"
        )
    )

    # Contact Section
    contact = Div(
        H2("Still need help?", style="margin-bottom:1.5rem;border-bottom:1px solid var(--color-border);padding-bottom:0.5rem"),
        Div(
            P("Our support team is here for you. We usually respond within 24 hours.", style="margin-bottom:1.5rem"),
            A(
                Button("Contact Support", cls="button button-primary"),
                href="mailto:support@okenaba.com",
                style="text-decoration:none"
            ),
            cls="contact-box",
            style="background:var(--color-secondary);padding:2rem;border-radius:var(--radius-lg);text-align:center"
        )
    )

    content = Div(
        hero,
        guides,
        faq,
        contact,
        cls="help-content",
        style="max-width:800px;margin:0 auto"
    )

    return page_layout(content, user=user, title="Okenaba - Help Center", active_nav="help")


def _guide_card(title, desc, link):
    return A(
        H3(title, style="font-size:1.1rem;margin-bottom:0.5rem;color:var(--color-primary)"),
        P(desc, style="color:var(--color-text-light);font-size:0.9rem"),
        href=link,
        style="display:block;padding:1.5rem;border:1px solid var(--color-border);border-radius:var(--radius-md);text-decoration:none;transition:var(--transition);background:var(--color-background)",
        cls="guide-card"
    )

def _faq_item(question, answer):
    return Div(
        H3(question, style="font-size:1rem;margin-bottom:0.25rem"),
        P(answer, style="color:var(--color-text-light);font-size:0.95rem"),
        style="padding:1rem;background:var(--color-background);border-radius:var(--radius-md);border:1px solid var(--color-border)"
    )
