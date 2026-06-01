"""Help page — Guides, FAQ, and Support."""

from fasthtml.common import Div, H1, H2, H3, P, A, Button
from user_app.frontend.layout import page_layout


def help_page(user):
    hero = Div(
        H1("How can we help you?", cls="help-hero-title"),
        P("Find answers, read guides, or get in touch.", cls="help-hero-sub"),
        cls="help-hero",
    )

    guides = Div(
        H2("Guides & Tutorials", cls="help-section-head"),
        Div(
            _guide_card("Getting Started",         "Learn the basics of Okenaba and how to set up your account.", "#"),
            _guide_card("Creating Your First Site", "Step-by-step walkthrough of the site generation process.", "#"),
            _guide_card("Editing Content",          "How to use the editor to customize your website text and images.", "#"),
            _guide_card("Publishing & Domains",     "Go live with your site and connect custom domains.", "#"),
            cls="guide-grid",
        ),
        cls="help-section",
    )

    faq = Div(
        H2("Frequently Asked Questions", cls="help-section-head"),
        Div(
            _faq_item("Is Okenaba free to use?",
                      "Okenaba gives you 1 free credit on signup — no card required. After that, buy only the credits you need. There are no subscriptions."),
            _faq_item("Can I use my own domain?",
                      "Yes! You can connect any custom domain you own to your published Okenaba site."),
            _faq_item("How do I cancel or manage my credits?",
                      "Credits never expire — there's nothing to cancel. You can manage everything from the Credits page in your account."),
            _faq_item("What if I don't like the generated site?",
                      "You can edit any text, swap images, or change colors directly in the editor. You can also regenerate with a new prompt at no extra cost."),
            cls="faq-list",
        ),
        cls="help-section",
    )

    contact = Div(
        H2("Still need help?", cls="help-section-head"),
        Div(
            P("Our support team is here for you. We usually respond within 24 hours."),
            A(
                Button("Contact Support", cls="button button-primary"),
                href="mailto:support@okenaba.com",
                style="text-decoration:none",
            ),
            cls="contact-box",
        ),
        cls="help-section",
    )

    content = Div(hero, guides, faq, contact, cls="help-content")
    return page_layout(content, user=user, title="Okenaba - Help Center", active_nav="help")


def _guide_card(title, desc, link):
    return A(
        H3(title, cls="guide-card-title"),
        P(desc,   cls="guide-card-desc"),
        href=link,
        cls="guide-card",
    )


def _faq_item(question, answer):
    return Div(
        H3(question, cls="faq-question"),
        P(answer,    cls="faq-answer"),
        cls="faq-item",
    )
