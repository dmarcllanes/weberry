// ── Cosmic Starfield Canvas ────────────────────────────────
(function () {
    var canvas = document.getElementById('cosmos-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var W, H, stars, lastTime = 0, shootCooldown = 0;
    var shooters = [];

    function rand(a, b) { return a + Math.random() * (b - a); }

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function makeStars() {
        var n = Math.floor(W * H / 3800);
        stars = [];
        for (var i = 0; i < n; i++) {
            stars.push({
                x: Math.random() * W,
                y: Math.random() * H,
                r: rand(0.3, 1.8),
                b: Math.random(),          // brightness phase
                db: rand(0.003, 0.013),    // brightness delta
                col: Math.random() > 0.82 ? '#93c5fd'
                   : Math.random() > 0.90 ? '#93c5fd'
                   : '#ffffff',
            });
        }
    }

    function addShooter() {
        var angle = rand(22, 48) * Math.PI / 180;
        shooters.push({
            x: rand(0, W * 0.65),
            y: rand(0, H * 0.45),
            angle: angle,
            len: rand(110, 240),
            spd: rand(700, 1300),
            t: 0,
        });
    }

    function frame(ts) {
        var dt = Math.min((ts - lastTime) / 1000, 0.05);
        lastTime = ts;

        ctx.clearRect(0, 0, W, H);

        // Stars
        for (var i = 0; i < stars.length; i++) {
            var s = stars[i];
            s.b += s.db;
            if (s.b > 1 || s.b < 0) s.db = -s.db;
            var a = 0.12 + s.b * 0.88;
            ctx.globalAlpha = a;
            ctx.fillStyle = s.col;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();
            // Soft glow on bigger stars
            if (s.r > 1.3 && s.b > 0.65) {
                ctx.globalAlpha = a * 0.1;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r * 5, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.globalAlpha = 1;

        // Spawn shooting star
        shootCooldown -= dt;
        if (shootCooldown <= 0) {
            addShooter();
            shootCooldown = rand(5, 11);
        }

        // Draw shooting stars
        for (var j = shooters.length - 1; j >= 0; j--) {
            var sh = shooters[j];
            sh.t += dt * sh.spd;
            var progress = sh.t / (sh.len * 2.2);
            if (progress > 1) { shooters.splice(j, 1); continue; }

            var fade = progress < 0.25 ? progress / 0.25
                     : progress > 0.7  ? (1 - progress) / 0.3
                     : 1;

            var hx = sh.x + Math.cos(sh.angle) * sh.t;
            var hy = sh.y + Math.sin(sh.angle) * sh.t;
            var tx = hx - Math.cos(sh.angle) * sh.len;
            var ty = hy - Math.sin(sh.angle) * sh.len;

            var g = ctx.createLinearGradient(tx, ty, hx, hy);
            g.addColorStop(0, 'rgba(255,255,255,0)');
            g.addColorStop(0.7, 'rgba(196,181,253,' + (fade * 0.6) + ')');
            g.addColorStop(1, 'rgba(255,255,255,' + (fade * 0.95) + ')');

            ctx.strokeStyle = g;
            ctx.lineWidth = 1.4;
            ctx.beginPath();
            ctx.moveTo(tx, ty);
            ctx.lineTo(hx, hy);
            ctx.stroke();
        }

        requestAnimationFrame(frame);
    }

    window.addEventListener('resize', function () { resize(); makeStars(); });
    resize();
    makeStars();
    requestAnimationFrame(frame);
})();

// ── Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ── Navbar scrolled class
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    }
}, { passive: true });

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

// ── Scroll progress bar ──────────────────────────────────────
(function () {
    var bar = document.getElementById('scroll-progress');
    if (!bar) return;
    function updateProgress() {
        var scrollTop = window.scrollY;
        var docHeight = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (docHeight > 0 ? (scrollTop / docHeight) * 100 : 0) + '%';
    }
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
})();

// ── CSS-class reveal system (replaces old inline-style observer) ─
(function () {
    // Auto-add reveal class to cards, steps, and headings
    var autoReveal = [
        ['.feature-card',      'reveal',       120],
        ['.pricing-card',      'reveal-scale', 110],
        ['.testimonial-card',  'reveal',       130],
        ['.step',              'reveal',       120],
        ['.stat-item',         'reveal-scale', 90],
        ['.pvo-card',          'reveal-scale', 180],
        ['.sc-card',           'reveal',       90],
        ['.zs-step',           'reveal',       140],
        ['.comp-card',         'reveal-scale', 130],
        ['.faq-item',          'reveal',       70],
        ['.section-eyebrow',   'reveal',       0],
        ['.features h2, .how-it-works h2, .pricing h2, .testimonials h2, .stats h2, .pain-vs-orbit h2, .showcase h2, .zero-skills h2, .comparison h2, .faq-section h2', 'reveal', 0],
    ];

    autoReveal.forEach(function(rule) {
        var selector = rule[0], cls = rule[1], baseDelay = rule[2];
        document.querySelectorAll(selector).forEach(function(el, i) {
            el.classList.add(cls);
            el.style.setProperty('--reveal-delay', (i * baseDelay) + 'ms');
        });
    });

    // Also handle explicit .section-underline
    document.querySelectorAll('.section-underline').forEach(function(el) {
        el.classList.add('reveal');
    });

    // Observe everything with a reveal class
    var revealObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale, .section-underline').forEach(function(el) {
        revealObserver.observe(el);
    });
})();

// ── Parallax: planet + nebula blobs on scroll ────────────────
(function () {
    var heroVisual = document.querySelector('.hero-visual');
    var blobs = document.querySelectorAll('.nebula-blob');

    window.addEventListener('scroll', function () {
        var sy = window.scrollY;
        if (heroVisual) {
            heroVisual.style.transform = 'translateY(' + (sy * 0.07) + 'px)';
        }
        blobs.forEach(function (blob, i) {
            var speed = [0.025, -0.02, 0.035, -0.015][i % 4];
            blob.style.transform = 'translateY(' + (sy * speed) + 'px)';
        });
    }, { passive: true });
})();

// ── Cursor comet trail ────────────────────────────────────────
(function () {
    var colors = ['#93c5fd', '#3b82f6', '#2563eb', '#60a5fa', '#bfdbfe'];
    var sizes  = [5, 4, 3, 6, 4];

    document.addEventListener('mousemove', function (e) {
        var dot = document.createElement('div');
        dot.className = 'cursor-comet';
        var idx = Math.floor(Math.random() * colors.length);
        var sz  = sizes[idx];
        dot.style.cssText = [
            'left:' + e.clientX + 'px',
            'top:' + e.clientY + 'px',
            'width:' + sz + 'px',
            'height:' + sz + 'px',
            'background:' + colors[idx],
            'box-shadow:0 0 ' + (sz * 3) + 'px ' + colors[idx],
        ].join(';');
        document.body.appendChild(dot);
        setTimeout(function () { dot.parentNode && dot.parentNode.removeChild(dot); }, 560);
    });
})();

// ── Magnetic buttons: primary CTAs follow cursor ─────────────
(function () {
    document.querySelectorAll('.btn-primary').forEach(function (btn) {
        btn.addEventListener('mousemove', function (e) {
            var rect = btn.getBoundingClientRect();
            var dx = e.clientX - (rect.left + rect.width  / 2);
            var dy = e.clientY - (rect.top  + rect.height / 2);
            btn.style.transform = 'translate(' + dx * 0.14 + 'px,' + dy * 0.14 + 'px) translateY(-2px)';
        });
        btn.addEventListener('mouseleave', function () {
            btn.style.transform = '';
        });
    });
})();

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

// Cookie Banner
document.getElementById('cookie-accept').addEventListener('click', function () {
    document.getElementById('cookie-banner').style.display = 'none';
});
document.getElementById('cookie-decline').addEventListener('click', function () {
    document.getElementById('cookie-banner').style.display = 'none';
});

// Survey Submit
async function surveySubmit(e) {
    e.preventDefault();
    var form = e.currentTarget;
    var card = document.querySelector('.survey-card');
    if (!card) return;

    var btn = form.querySelector('.survey-submit');
    if (btn) { btn.disabled = true; btn.style.opacity = '0.6'; }

    try {
        await fetch('/api/survey', { method: 'POST', body: new FormData(form) });
    } catch (_) {}

    card.classList.add('survey--sent');
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Billing Toggle
function toggleBilling() {
    const isYearly = document.getElementById('billing-toggle').checked;
    const monthlyPrices = document.querySelectorAll('.price-monthly');
    const yearlyPrices = document.querySelectorAll('.price-yearly');
    const labelMonthly = document.getElementById('label-monthly');
    const labelYearly = document.getElementById('label-yearly');

    if (isYearly) {
        monthlyPrices.forEach(el => el.style.display = 'none');
        yearlyPrices.forEach(el => el.style.display = 'block');
        labelMonthly.classList.remove('active');
        labelYearly.classList.add('active');
    } else {
        monthlyPrices.forEach(el => el.style.display = 'block');
        yearlyPrices.forEach(el => el.style.display = 'none');
        labelMonthly.classList.add('active');
        labelYearly.classList.remove('active');
    }
}
