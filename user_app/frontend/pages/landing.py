from fasthtml.common import *
from fasthtml.svg import * # Make sure Svg, Path, etc are available

from user_app.frontend.layout import page_layout
from config.settings import SUPABASE_URL, SUPABASE_KEY


def landing_page():
    return Html(
    Head(
        Meta(charset='UTF-8'),
        Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        Title('Okenaba - Build AI Websites in Minutes'),
        Link(rel='icon', type='image/svg+xml', href='/static/img/favicon.svg'),
        Link(rel='stylesheet', href='/static/css/landing.css?v=8'),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap", rel="stylesheet"),
        Script(src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"),
        Script(f"window.SUPABASE_URL='{SUPABASE_URL}';window.SUPABASE_KEY='{SUPABASE_KEY}';"),
        Script(src='/static/js/auth_check.js'),
    ),
    Body(
        Div(
            Div(
                Span("🚀 Launch Special: Build your dream site in minutes! "),
                Span("✨ New AI features just dropped! "),
                Span("🔥 Join 10,000+ creators on Okenaba. "),
                Span("🚀 Launch Special: Build your dream site in minutes! "),
                Span("✨ New AI features just dropped! "),
                Span("🔥 Join 10,000+ creators on Okenaba. "),
                cls='marquee-content'
            ),
            cls='announcement-banner'
        ),
        Nav(
            Div(
                Div(
                    Div('Okenaba', cls='logo'),
                    
                    # Desktop Nav
                    Ul(
                        Li(A('Features', href='#features')),
                        Li(A('How It Works', href='#how-it-works')),
                        Li(A('Pricing', href='#pricing')),
                        Li(A('Contact', href='#contact')),
                        cls='nav-links'
                    ),
                    
                    Div(
                        A('Sign In', cls='btn-secondary', href='/login'),
                        
                        # Mobile Menu Toggle
                        Button(
                            Span(cls='bar'),
                            Span(cls='bar'),
                            Span(cls='bar'),
                            cls='mobile-menu-btn',
                            onclick='toggleMobileMenu()'
                        ),
                        cls='nav-actions'
                    ),

                    cls='nav-content'
                ),
                
                # Mobile Menu Dropdown
                Div(
                    Ul(
                        Li(A('Features', href='#features', onclick='toggleMobileMenu()')),
                        Li(A('How It Works', href='#how-it-works', onclick='toggleMobileMenu()')),
                        Li(A('Pricing', href='#pricing', onclick='toggleMobileMenu()')),
                        Li(A('Contact', href='#contact', onclick='toggleMobileMenu()')),
                        Li(A('Sign In', href='/login', cls='mobile-nav-cta')),
                        cls='mobile-nav-links'
                    ),
                    cls='mobile-menu',
                    id='mobileMenu'
                ),
                
                cls='container'
            ),
            cls='navbar'
        ),
        Header(
            Div(
                Div(
                    H1('Build Your Dream Website in Minutes with AI', cls='hero-title'),
                    P('No coding required. Just describe your business and let Okenaba do the rest.\n                    Your professional online presence is one click away.', cls='hero-subtitle'),
                    Div(
                        A('Start Building For Free', cls='btn-primary', href='/login'),
                        A('View Examples', cls='btn-secondary', href='#features'),
                        cls='hero-buttons'
                    ),
                    cls='hero-content'
                ),
                Div(
                    Div(cls='gradient-box'),
                    cls='hero-visual'
                ),
                cls='container'
            ),
            cls='hero'
        ),
        Section(
            Div(
                P('Powering next-gen businesses and creators', cls='proof-label'),
                Div(
                    Div(
                        # First set of logos
                        Img(src='/static/img/brands/amazon.svg', alt='Amazon', cls='brand-logo'),
                        Img(src='/static/img/brands/facebook.svg', alt='Facebook', cls='brand-logo'),
                        Img(src='/static/img/brands/puma.svg', alt='Puma', cls='brand-logo'),
                        Img(src='/static/img/brands/lamborghini.svg', alt='Lamborghini', cls='brand-logo'),
                        Img(src='/static/img/brands/gucci.svg', alt='Gucci', cls='brand-logo'),
                        Img(src='/static/img/brands/pedigree.svg', alt='Pedigree', cls='brand-logo'),
                        # Duplicate for seamless scroll
                        Img(src='/static/img/brands/amazon.svg', alt='Amazon', cls='brand-logo'),
                        Img(src='/static/img/brands/facebook.svg', alt='Facebook', cls='brand-logo'),
                        Img(src='/static/img/brands/puma.svg', alt='Puma', cls='brand-logo'),
                        Img(src='/static/img/brands/lamborghini.svg', alt='Lamborghini', cls='brand-logo'),
                        Img(src='/static/img/brands/gucci.svg', alt='Gucci', cls='brand-logo'),
                        Img(src='/static/img/brands/pedigree.svg', alt='Pedigree', cls='brand-logo'),
                        cls='marquee-track'
                    ),
                    cls='brand-marquee'
                ),
                cls='container'
            ),
            cls='social-proof'
        ),
        Section(
            Div(
                H2('Everything You Need to Scale'),
                Div(
                    Div(
                        Div(
                            # Zap Icon
                            Svg(Path(d='M13 2L3 14h9l-1 8 10-12h-9l1-8z'), viewBox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round'),
                            cls='feature-icon-wrapper'
                        ),
                        H3('Blazing Fast Speed'),
                        P('Go from prompt to published website in under 60 seconds. Our AI generates structure, copy, and images instantly.'),
                        cls='feature-card bento-wide'
                    ),
                    Div(
                        Div(
                            # Palette Icon
                            Svg(Path(d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'), viewBox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round'),
                            cls='feature-icon-wrapper'
                        ),
                        H3('Professional Design'),
                        P('Get premium, designer-quality layouts automatically.'),
                        cls='feature-card'
                    ),
                    Div(
                        Div(
                            # Line Chart Icon (SEO)
                            Svg(Path(d='M23 6l-9.5 9.5-5-5L1 18'), Path(d='M17 6h6v6'), viewBox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round'),
                            cls='feature-icon-wrapper'
                        ),
                        H3('SEO Optimized'),
                        P('Rank higher with built-in technical SEO and tags.'),
                        cls='feature-card'
                    ),
                    Div(
                        Div(
                            # Smartphone Icon
                            Svg(Rect(x='5', y='2', width='14', height='20', rx='2', ry='2'), Line(x1='12', y1='18', x2='12.01', y2='18'), viewBox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round'),
                            cls='feature-icon-wrapper'
                        ),
                        H3('Mobile Responsive'),
                        P('Your site will look perfect on every device automatically.'),
                        cls='feature-card bento-wide'
                    ),
                    cls='bento-grid'
                ),
                cls='container'
            ),
            id='features',
            cls='features'
        ),
        Section(
                Div(
                    H2('From Idea to Launch in 4 Steps'),
                    Div(
                        Div(
                            Div('01', cls='step-number'),
                            H3('Describe Your Vision'),
                            P('Simply type a few sentences describing your business, your style, and your goals. No technical jargon needed.'),
                            cls='step'
                        ),
                        Div(
                            Div('02', cls='step-number'),
                            H3('AI Generates Site'),
                            P('Our advanced AI engine analyzes your request and builds a complete, unique website structure with relevant content.'),
                            cls='step'
                        ),
                        Div(
                            Div('03', cls='step-number'),
                            H3('Customize Details'),
                            P('Use our intuitive editor to tweak colors, images, and text. Regenerate sections with a click until it\'s perfect.'),
                            cls='step'
                        ),
                        Div(
                            Div('04', cls='step-number'),
                            H3('Publish & Grow'),
                            P('Connect your domain and go live instantly. Access your dashboard to manage updates and track your success.'),
                            cls='step'
                        ),
                        cls='steps'
                    ),
                    cls='container'
                ),
            id='how-it-works',
            cls='how-it-works'
        ),
        Section(
            Div(
                Div(
                    H4('98%'),
                    P('Success Rate'),
                    cls='stat-item'
                ),
                Div(
                    H4('48 hours'),
                    P('Average to First Feedback'),
                    cls='stat-item'
                ),
                Div(
                    H4('$2.3M'),
                    P('Total Funding Raised'),
                    cls='stat-item'
                ),
                Div(
                    H4('50+'),
                    P('Successful Launches'),
                    cls='stat-item'
                ),
                cls='container'
            ),
            cls='stats'
        ),
        Section(
            Div(
                Div(
                    H2('Simple Pricing', cls='text-glow'),
                    P('Start small and scale as you grow.', cls='section-subtitle'),
                    
                    Div(
                        Span('✨ 7 Days Free Trial', cls='badge-save', style='margin:0 0 1rem 0;display:inline-block'),
                        style='text-align:center'
                    ),

                    # Billing Toggle
                    Div(
                        Span('Monthly', cls='billing-label active', id='label-monthly'),
                        Label(
                            Input(type='checkbox', id='billing-toggle', onclick='toggleBilling()'),
                            Span(cls='slider round'),
                            cls='switch'
                        ),
                        Span('Yearly', cls='billing-label', id='label-yearly'),
                        cls='pricing-toggle-container'
                    ),
                    cls='pricing-header'
                ),
                
                Div(
                    # Small Plan
                    Div(
                        H3('Small'),
                        Div(
                            # Monthly Price
                            Div(
                                H4('$10', cls='price-amount'),
                                Span('/month', cls='price-period'),
                                cls='price-display price-monthly'
                            ),
                            # Yearly Price
                            Div(
                                H4('$100', cls='price-amount'),
                                Span('/year', cls='price-period'),
                                P('$8.33/mo', cls='price-subtext'),
                                cls='price-display price-yearly',
                                style='display:none'
                            ),
                            cls='price-wrapper'
                        ),
                        P('Perfect for hobbyists and checking out the platform.', cls='plan-desc'),
                        Ul(
                            Li('✓ 10 Pages'),
                            Li('✓ Basic Analytics'),
                            Li('✓ Community Support'),
                            Li('✓ Export to HTML/CSS'),
                            cls='features-list'
                        ),
                        A('Get Started', cls='btn-secondary', href='/login'),
                        cls='pricing-card'
                    ),
                    
                    # Medium Plan
                    Div(
                        Span('Most Popular', cls='badge'),
                        H3('Medium'),
                        Div(
                            # Monthly Price
                            Div(
                                H4('$30', cls='price-amount'),
                                Span('/month', cls='price-period'),
                                cls='price-display price-monthly'
                            ),
                            # Yearly Price
                            Div(
                                H4('$300', cls='price-amount'),
                                Span('/year', cls='price-period'),
                                P('$25/mo', cls='price-subtext'),
                                cls='price-display price-yearly',
                                style='display:none'
                            ),
                            cls='price-wrapper'
                        ),
                        P('For freelancers and creators building multiple sites.', cls='plan-desc'),
                        Ul(
                            Li('✓ 40 Pages'),
                            Li('✓ Advanced Analytics'),
                            Li('✓ Priority Support'),
                            Li('✓ Remove Branding'),
                            Li('✓ Custom Domain'),
                            cls='features-list'
                        ),
                        A('Start Free Trial', cls='btn-primary', href='/login'),
                        cls='pricing-card featured'
                    ),
                    
                    # Big Plan
                    Div(
                        H3('Big'),
                        Div(
                            # Monthly Price
                            Div(
                                H4('$80', cls='price-amount'),
                                Span('/month', cls='price-period'),
                                cls='price-display price-monthly'
                            ),
                            # Yearly Price
                            Div(
                                H4('$800', cls='price-amount'),
                                Span('/year', cls='price-period'),
                                P('$66/mo', cls='price-subtext'),
                                cls='price-display price-yearly',
                                style='display:none'
                            ),
                            cls='price-wrapper'
                        ),
                        P('For agencies and power users who need scale.', cls='plan-desc'),
                        Ul(
                            Li('✓ 100 Pages'),
                            Li('✓ Team Collaboration'),
                            Li('✓ White Labeling'),
                            Li('✓ Dedicated Success Manager'),
                            Li('✓ API Access'),
                            cls='features-list'
                        ),
                        A('Contact Sales', cls='btn-secondary', href='/login'),
                        cls='pricing-card'
                    ),
                    cls='pricing-grid'
                ),
                cls='container'
            ),
            id='pricing',
            cls='pricing'
        ),
        Section(
            Div(
                Div(
                    H2('Tell Us About Your Business'),
                    P('Help us tailor Okenaba to your needs. What kind of business are you building?', cls='section-subtitle'),
                    
                    Form(
                        Div(
                            Label('Business Name', cls='form-label'),
                            Input(type='text', name='business_name', placeholder='e.g. Acme Corp', cls='form-input'),
                            cls='form-group'
                        ),
                        Div(
                            Label('Industry', cls='form-label'),
                            Select(
                                Option('Select an industry...', value='', disabled=True, selected=True),
                                Option('Technology', value='tech'),
                                Option('E-commerce', value='ecommerce'),
                                Option('Professional Services', value='services'),
                                Option('Creative & Design', value='creative'),
                                Option('Health & Wellness', value='health'),
                                Option('Other', value='other'),
                                name='industry',
                                cls='form-select'
                            ),
                            cls='form-group'
                        ),
                        Div(
                            Label('Business Description', cls='form-label'),
                            Textarea(name='description', placeholder='Briefly describe what your business does...', cls='form-textarea', rows='4'),
                            cls='form-group'
                        ),
                        Button('Submit Details', cls='btn-primary', style='width:100%'),
                        cls='survey-form',
                        onclick="alert('Thank you! We will use this to improve our templates.'); return false;"
                    ),
                    cls='survey-container'
                ),
                cls='container'
            ),
            id='business-survey',
            cls='survey-section'
        ),
        Section(
                Div(
                    H2('What Creators Say'),
                    Div(
                        Div(
                            Div(
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                cls='stars'
                            ),
                            P('"Okenaba helped me validate my SaaS concept before building. I saved 6 months and $50k!"', cls='testimonial-text'),
                            Div(
                                Div('SC', cls='avatar-placeholder', style='background: linear-gradient(135deg, #FF6B6B, #EE5D5D)'),
                                Div(
                                    P('Sarah Chen', cls='author-name'),
                                    P('Founder, TechFlow', cls='author-role'),
                                    cls='author-info'
                                ),
                                cls='testimonial-author'
                            ),
                            cls='testimonial-card'
                        ),
                        Div(
                            Div(
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                cls='stars'
                            ),
                            P('"The community feedback was invaluable. I pivoted my product and it\'s now 3x more successful."', cls='testimonial-text'),
                            Div(
                                Div('MJ', cls='avatar-placeholder', style='background: linear-gradient(135deg, #4ECDC4, #45B7AF)'),
                                Div(
                                    P('Marcus Johnson', cls='author-name'),
                                    P('Entrepreneur', cls='author-role'),
                                    cls='author-info'
                                ),
                                cls='testimonial-author'
                            ),
                            cls='testimonial-card'
                        ),
                        Div(
                            Div(
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                Svg(Path(d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'), viewBox='0 0 24 24', fill='#fbbf24', stroke='none', cls='icon-star'),
                                cls='stars'
                            ),
                            P('"Built my online identity from zero to a recognized brand in 3 months. Highly recommend!"', cls='testimonial-text'),
                            Div(
                                Div('AR', cls='avatar-placeholder', style='background: linear-gradient(135deg, #a78bfa, #8b5cf6)'),
                                Div(
                                    P('Alex Rivera', cls='author-name'),
                                    P('Creator', cls='author-role'),
                                    cls='author-info'
                                ),
                                cls='testimonial-author'
                            ),
                            cls='testimonial-card'
                        ),
                        cls='testimonials-grid'
                    ),
                    cls='container'
                ),
            cls='testimonials'
        ),
        Section(
            Div(
                H2('Ready to Join the Future of Building?'),
                P('Join 15,000+ creators building the next generation of the web with Okenaba.'),
                Button('Get Started for Free', cls='btn-primary'),
                cls='container cta-content'
            ),
            id='cta',
            cls='cta'
        ),

        Footer(
            Div(
                Div(
                    Div(
                        H4('Okenaba'),
                        P('Build your professional online presence with AI. Fast, beautiful, and effortless.'),
                        cls='footer-section'
                    ),
                    Div(
                        H4('Product'),
                        Ul(
                            Li(
                                A('Features', href='#features')
                            ),
                            Li(
                                A('Pricing', href='#pricing')
                            ),
                            Li(
                                A('Blog', href='#')
                            )
                        ),
                        cls='footer-section'
                    ),
                    Div(
                        H4('Company'),
                        Ul(
                            Li(
                                A('About', href='#')
                            ),
                            Li(
                                A('Careers', href='#')
                            ),
                            Li(
                                A('Contact', href='#')
                            )
                        ),
                        cls='footer-section'
                    ),
                    Div(
                        H4('Legal'),
                        Ul(
                            Li(
                                A('Privacy', href='#')
                            ),
                            Li(
                                A('Terms', href='#')
                            ),
                            Li(
                                A('Security', href='#')
                            )
                        ),
                        cls='footer-section'
                    ),
                    cls='footer-content'
                ),
                Div(
                    P('© 2024 Okenaba. All rights reserved.'),
                    Div(
                        A(Img(src='/static/img/brands/twitter.svg', alt='Twitter'), href='#'),
                        A(Img(src='/static/img/brands/linkedin.svg', alt='LinkedIn'), href='#'),
                        A(Img(src='/static/img/brands/discord.svg', alt='Discord'), href='#'),
                        cls='social-links'
                    ),
                    cls='footer-bottom'
                ),
                cls='container'
            ),
            cls='footer'
        ),
        Script(src='/static/js/landing.js')
    ),
    lang='en'
)