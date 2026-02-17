// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add scroll effect to navbar
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.borderBottomColor = 'rgba(51, 51, 51, 0.5)';
    } else {
        navbar.style.borderBottomColor = '#333333';
    }
});

// Button click handlers with visual feedback
document.querySelectorAll('.btn-primary, .btn-secondary').forEach(button => {
    button.addEventListener('click', function (e) {
        // Create ripple effect
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.5)';
        ripple.style.pointerEvents = 'none';
        ripple.style.animation = 'ripple-animation 0.6s ease-out';

        // Add ripple animation
        const style = document.createElement('style');
        if (!document.querySelector('style[data-ripple]')) {
            style.setAttribute('data-ripple', 'true');
            style.textContent = `
                @keyframes ripple-animation {
                    from {
                        transform: scale(0);
                        opacity: 1;
                    }
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);

        // Remove ripple after animation
        setTimeout(() => ripple.remove(), 600);
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe feature cards, pricing cards, and testimonials
document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card, .step').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Form submission handler (for CTA buttons)
document.querySelectorAll('button[class*="btn"]').forEach(button => {
    button.addEventListener('click', function () {
        const buttonText = this.textContent.trim();

        if (buttonText.includes('Free Trial') || buttonText.includes('Get Started') || buttonText.includes('Today')) {
            console.log('Free trial signup clicked');
            // You can add modal or form submission logic here
        }

        if (buttonText.includes('Watch Demo')) {
            console.log('Demo requested');
            // You can add video modal or redirect logic here
        }

        if (buttonText.includes('Contact Sales')) {
            console.log('Contact sales clicked');
            // You can add contact form logic here
        }

        if (buttonText.includes('Sign In')) {
            console.log('Sign in clicked');
            // You can add sign in modal logic here
        }
    });
});

// Add counter animation for stats section
const animateCounters = () => {
    const stats = document.querySelectorAll('.stat-item h4');
    const duration = 1500;

    stats.forEach(stat => {
        // Strip non-numeric chars except period for float parsing
        const rawText = stat.textContent;
        const target = parseFloat(rawText.replace(/[^0-9.]/g, ''));
        const isPercentage = rawText.includes('%');
        const isCurrency = rawText.includes('$');
        const isDecimal = !Number.isInteger(target);

        let current = 0;
        const startTime = Date.now();

        const updateCount = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            let value;
            if (isDecimal) {
                value = (target * progress).toFixed(1);
            } else {
                value = Math.floor(target * progress);
            }

            if (isPercentage) {
                stat.textContent = value + '%';
            } else if (rawText.includes('days')) {
                stat.textContent = value + ' days';
            } else if (rawText.includes('hours')) {
                stat.textContent = value + ' hours';
            } else if (isCurrency) {
                stat.textContent = '$' + value + 'M';
            } else {
                stat.textContent = value + '+';
            }

            if (progress < 1) {
                requestAnimationFrame(updateCount);
            }
        };

        updateCount();
    });
};

// Trigger counter animation when stats section is visible
const statsSection = document.querySelector('.stats');
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

if (statsSection) {
    statsObserver.observe(statsSection);
}

// Mobile menu toggle (for future expansion)
const setupMobileMenu = () => {
    // Add mobile menu functionality here if needed
    const navBar = document.querySelector('.navbar');
    const isMobile = window.innerWidth < 768;

    if (isMobile) {
        console.log('Mobile view activated');
    }
};

window.addEventListener('resize', setupMobileMenu);
setupMobileMenu();

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close any open modals/dropdowns if implemented
        console.log('Escape key pressed');
    }
});

// Prevent layout shift on scroll
document.addEventListener('DOMContentLoaded', () => {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.scrollbarGutter = 'stable';
});

// Accessibility: Focus visible styling
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
});

// Add keyboard navigation styles
const style = document.createElement('style');
style.textContent = `
    body.keyboard-nav button:focus,
    body.keyboard-nav a:focus {
        outline: 2px solid #0066ff;
        outline-offset: 2px;
    }
    
    button:focus-visible,
    a:focus-visible {
        outline: 2px solid #0066ff;
        outline-offset: 2px;
    }
`;
document.head.appendChild(style);

console.log('IdeaVault landing page loaded successfully!');

// Mobile Menu Toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const btn = document.querySelector('.mobile-menu-btn');

    if (menu && btn) {
        menu.classList.toggle('active');
        btn.classList.toggle('active');
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('mobileMenu');
    const btn = document.querySelector('.mobile-menu-btn');

    if (menu && btn && menu.classList.contains('active')) {
        if (!menu.contains(e.target) && !btn.contains(e.target)) {
            menu.classList.remove('active');
            btn.classList.remove('active');
        }
    }
});
