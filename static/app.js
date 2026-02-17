// Okenaba - Client-side step navigation and utilities

document.addEventListener('DOMContentLoaded', function () {
    updateStepIndicator();
    updatePreview();
    initOnboardingExitGuard();
    initTheme();

    // Keyboard navigation: Enter advances step (except on textarea/button)
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            var tag = e.target.tagName.toLowerCase();
            if (tag === 'textarea' || tag === 'button') return;

            // Allow Enter/Space on step indicator circles
            if (e.target.classList.contains('si-circle') && e.target.classList.contains('si-completed')) {
                e.target.click();
                return;
            }

            var wizard = document.querySelector('.wizard');
            if (!wizard) return;

            e.preventDefault();
            if (currentStep < totalSteps) {
                nextStep();
            }
        }
        if (e.key === ' ' && e.target.classList.contains('si-circle') && e.target.classList.contains('si-completed')) {
            e.preventDefault();
            e.target.click();
        }
    });
});

// --- Mobile Navigation ---

function toggleMobileMenu() {
    var nav = document.getElementById('main-nav');
    var toggle = document.querySelector('.mobile-toggle');
    if (nav) {
        nav.classList.toggle('nav-open');
        toggle.classList.toggle('active');
        // Prevent scrolling when menu is open
        document.body.style.overflow = nav.classList.contains('nav-open') ? 'hidden' : '';
    }
}

function toggleUserMenu() {
    var menu = document.getElementById('user-dropdown');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function (e) {
    if (!e.target.closest('.user-menu-container')) {
        var menu = document.getElementById('user-dropdown');
        if (menu && menu.classList.contains('show')) {
            menu.classList.remove('show');
        }
    }
});

// --- Step Navigation ---

var currentStep = 1;
var totalSteps = 3;
var isTransitioning = false;

function nextStep(event) {
    if (event) event.preventDefault();
    if (isTransitioning) return;
    if (!validateCurrentStep()) return;

    if (currentStep < totalSteps) {
        currentStep++;
        updateUI('forward');
    }
}

function prevStep() {
    if (isTransitioning) return;
    if (currentStep > 1) {
        currentStep--;
        updateUI('backward');
    }
}

function goToStep(step) {
    if (isTransitioning) return;
    if (step >= 1 && step <= totalSteps && step !== currentStep) {
        var direction = step > currentStep ? 'forward' : 'backward';
        currentStep = step;
        updateUI(direction);
    }
}

function updateUI(direction) {
    var wizard = document.querySelector('.wizard');
    if (!wizard) {
        // Fallback for non-wizard pages
        var steps = document.querySelectorAll('.step');
        steps.forEach(function (s) { s.classList.remove('step-active'); });
        var current = document.getElementById('step' + currentStep);
        if (current) current.classList.add('step-active');
        updateStepIndicator();
        updatePreview();
        return;
    }

    isTransitioning = true;

    var steps = wizard.querySelectorAll(':scope > .step');
    var oldStep = wizard.querySelector(':scope > .step.step-active');
    var newStep = document.getElementById('step' + currentStep);

    if (!newStep) {
        isTransitioning = false;
        return;
    }

    // Apply exit class to old step
    if (oldStep && oldStep !== newStep) {
        var exitClass = direction === 'forward' ? 'step-exit' : 'step-exit-reverse';
        oldStep.classList.remove('step-active');
        oldStep.classList.add(exitClass);

        // Clean up exit class after transition
        var cleanup = function () {
            oldStep.classList.remove(exitClass);
        };
        oldStep.addEventListener('transitionend', function handler() {
            oldStep.removeEventListener('transitionend', handler);
            cleanup();
        });
        // Safety timeout
        setTimeout(cleanup, 500);
    }

    // Activate new step with entry animation
    var entryTransform = direction === 'forward' ? 'translateX(30px)' : 'translateX(-30px)';
    newStep.style.transform = entryTransform;
    newStep.classList.add('step-active');

    // Force reflow then animate to final position
    newStep.offsetHeight;
    newStep.style.transform = '';

    // Clear transitioning guard
    setTimeout(function () {
        isTransitioning = false;
    }, 400);

    updateStepIndicator();
    updatePreview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateStepIndicator() {
    var indicator = document.getElementById('stepIndicator');
    if (!indicator) return;

    var circles = indicator.querySelectorAll('.si-circle');
    var connectors = indicator.querySelectorAll('.si-connector');
    var labels = indicator.querySelectorAll('.si-label');

    circles.forEach(function (circle, i) {
        var step = i + 1;
        circle.classList.remove('si-active', 'si-completed');

        if (step < currentStep) {
            circle.classList.add('si-completed');
            circle.setAttribute('tabindex', '0');
            circle.setAttribute('role', 'button');
            circle.style.cursor = 'pointer';
        } else if (step === currentStep) {
            circle.classList.add('si-active');
            circle.removeAttribute('tabindex');
            circle.removeAttribute('role');
            circle.style.cursor = '';
        } else {
            circle.removeAttribute('tabindex');
            circle.removeAttribute('role');
            circle.style.cursor = '';
        }
    });

    connectors.forEach(function (conn, i) {
        if (i + 1 < currentStep) {
            conn.classList.add('si-connector-done');
        } else {
            conn.classList.remove('si-connector-done');
        }
    });

    labels.forEach(function (label, i) {
        if (i + 1 <= currentStep) {
            label.classList.add('si-label-active');
        } else {
            label.classList.remove('si-label-active');
        }
    });
}

// --- Validation ---

function showFieldError(fieldId, msg) {
    var field = document.getElementById(fieldId);
    var errorSpan = document.getElementById(fieldId + '_error');
    if (field) field.classList.add('input-error');
    if (errorSpan) {
        errorSpan.textContent = msg;
        errorSpan.classList.add('field-error-visible');
    }
}

function clearFieldError(field) {
    field.classList.remove('input-error');
    var errorSpan = document.getElementById(field.id + '_error');
    if (errorSpan) {
        errorSpan.textContent = '';
        errorSpan.classList.remove('field-error-visible');
    }
}

function clearAllFieldErrors() {
    var errors = document.querySelectorAll('.field-error');
    errors.forEach(function (el) {
        el.textContent = '';
        el.classList.remove('field-error-visible');
    });
    var inputs = document.querySelectorAll('.input-error');
    inputs.forEach(function (el) {
        el.classList.remove('input-error');
    });
}

function validateCurrentStep() {
    clearAllFieldErrors();
    if (currentStep === 1) {
        var name = document.getElementById('business_name');
        if (name && !name.value.trim()) {
            showFieldError('business_name', 'Please enter your business name');
            name.focus();
            return false;
        }
        var industry = document.getElementById('industry');
        if (industry && !industry.value.trim()) {
            showFieldError('industry', 'Please enter your industry');
            industry.focus();
            return false;
        }
        var goal = document.getElementById('primary_goal');
        if (goal && !goal.value) {
            showFieldError('primary_goal', 'Please select a primary goal');
            goal.focus();
            return false;
        }
    }
    return true;
}

function validateBeforeSubmit() {
    clearAllFieldErrors();
    var name = document.getElementById('business_name');
    if (name && !name.value.trim()) {
        showFieldError('business_name', 'Business name is required');
        goToStep(1);
        name.focus();
        return false;
    }
    var industry = document.getElementById('industry');
    if (industry && !industry.value.trim()) {
        showFieldError('industry', 'Industry is required');
        goToStep(1);
        industry.focus();
        return false;
    }
    var goal = document.getElementById('primary_goal');
    if (goal && !goal.value) {
        showFieldError('primary_goal', 'Primary goal is required');
        goToStep(1);
        goal.focus();
        return false;
    }
    return true;
}

// --- Brain Dump Validation ---

function validateAndSubmit() {
    clearAllFieldErrors();
    var name = document.getElementById('business_name');
    if (name && !name.value.trim()) {
        showFieldError('business_name', 'Please enter your business name');
        goToStep(1);
        name.focus();
        return false;
    }
    var industry = document.getElementById('industry');
    if (industry && !industry.value.trim()) {
        showFieldError('industry', 'Please enter your industry');
        goToStep(1);
        industry.focus();
        return false;
    }
    var goal = document.getElementById('primary_goal');
    if (goal && !goal.value) {
        showFieldError('primary_goal', 'Please select a goal');
        goToStep(1);
        goal.focus();
        return false;
    }
    return showLoading('Building your site...');
}

// --- Preview ---

function updatePreview() {
    var previewContent = document.getElementById('previewContent');
    if (!previewContent) return;

    var name = document.getElementById('business_name');
    var tagline = document.getElementById('tagline');
    var desc = document.getElementById('description');
    var email = document.getElementById('contact_email');

    var nameVal = name ? name.value.trim() : '';
    var taglineVal = tagline ? tagline.value.trim() : '';
    var descVal = desc ? desc.value.trim() : '';
    var emailVal = email ? email.value.trim() : '';

    if (!nameVal && !taglineVal && !descVal) {
        previewContent.innerHTML =
            '<div class="preview-placeholder"><p>Your site preview will appear here</p></div>';
        return;
    }

    var html = '<div class="preview-site">';
    // Mini navbar bar
    html += '<div style="height:6px;background:' + 'var(--color-primary)' + ';border-radius:3px;opacity:0.3;margin-bottom:8px"></div>';
    // Hero section
    if (nameVal) {
        html += '<div class="preview-name">' + escapeHtml(nameVal) + '</div>';
    }
    if (taglineVal) {
        html += '<div class="preview-tagline">' + escapeHtml(taglineVal) + '</div>';
    }
    // Body content
    if (descVal) {
        html += '<div class="preview-bio">' + escapeHtml(descVal) + '</div>';
    }
    if (emailVal) {
        html += '<div class="preview-contact"><div class="preview-email">' + escapeHtml(emailVal) + '</div></div>';
    }
    // Mini footer bar
    html += '<div style="height:4px;background:var(--color-border);border-radius:2px;margin-top:12px"></div>';
    html += '</div>';
    previewContent.innerHTML = html;
}

// --- Clipboard ---

function copySiteLink(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
            showNotification('Link copied to clipboard!');
        });
    } else {
        var ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showNotification('Link copied to clipboard!');
    }
}

// --- Notifications ---

function showError(message) {
    showNotification(message, true);
}

function showNotification(message, isError) {
    var el = document.createElement('div');
    el.textContent = message;
    el.style.cssText =
        'position:fixed;top:20px;right:20px;' +
        'background-color:' + (isError ? '#EF4444' : '#10B981') + ';' +
        'color:white;padding:12px 20px;border-radius:8px;' +
        'box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:1000;' +
        'font-weight:600;transition:opacity 0.3s ease;';
    document.body.appendChild(el);
    setTimeout(function () {
        el.style.opacity = '0';
        setTimeout(function () { el.remove(); }, 300);
    }, 2500);
}

// --- Utilities ---

function escapeHtml(text) {
    var map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function (m) { return map[m]; });
}

// --- Loading Overlay ---

function showLoading(message) {
    var overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML =
        '<div class="loading-card">' +
        '<div class="loading-spinner"></div>' +
        '<div class="loading-message">' + escapeHtml(message) + '</div>' +
        '<div class="loading-subtext">This may take a moment</div>' +
        '</div>';
    document.body.appendChild(overlay);
    return true;
}

// --- Onboarding Exit Guard ---

function initOnboardingExitGuard() {
    var marker = document.getElementById('onboarding-active');
    if (!marker) return;

    var deleteUrl = marker.getAttribute('data-delete-url');

    // Warn on browser back / tab close
    window._onboardingBeforeUnload = function (e) {
        e.preventDefault();
        e.returnValue = '';
    };
    window.addEventListener('beforeunload', window._onboardingBeforeUnload);

    // Remove the guard when the braindump form is submitted (normal navigation)
    var form = marker.closest('form');
    if (form) {
        form.addEventListener('submit', function () {
            window.removeEventListener('beforeunload', window._onboardingBeforeUnload);
        });
    }

    // Intercept nav links — confirm then delete project before leaving
    var navLinks = document.querySelectorAll('.nav-link, .logo');
    navLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
                window.removeEventListener('beforeunload', window._onboardingBeforeUnload);
                submitDeleteAndRedirect(deleteUrl, link.getAttribute('href') || '/');
            }
        });
    });
}

function exitOnboarding(deleteUrl) {
    if (confirm('Are you sure you want to leave? This project will not be saved.')) {
        window.removeEventListener('beforeunload', window._onboardingBeforeUnload);
        submitDeleteAndRedirect(deleteUrl, '/');
    }
    return false;
}

// --- Asset Upload: reset file input and update counter after HTMX ---
document.addEventListener('htmx:afterRequest', function (evt) {
    var path = evt.detail.pathInfo && evt.detail.pathInfo.requestPath;
    if (path && path.indexOf('/assets') !== -1) {
        var fileInput = document.getElementById('asset-file');
        if (fileInput) fileInput.value = '';
        // Update counter
        var grid = document.getElementById('asset-list');
        var counter = document.getElementById('asset-counter');
        if (grid && counter) {
            var count = grid.querySelectorAll('.asset-card').length;
            counter.textContent = '(' + count + '/4)';
        }
    }
});

function submitDeleteAndRedirect(deleteUrl, redirectTo) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = deleteUrl;
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'redirect';
    input.value = redirectTo;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}

// --- Theme Toggle ---

function initTheme() {
    var storedTheme = localStorage.getItem('theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
        updateThemeIcon('light');
    }
}

function toggleTheme() {
    var currentTheme = document.documentElement.getAttribute('data-theme');
    var newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    if (newTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }

    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    var buttons = document.querySelectorAll('.theme-toggle');
    buttons.forEach(function (btn) {
        if (theme === 'dark') {
            // Moon icon
            btn.innerHTML = '🌙';
            btn.setAttribute('aria-label', 'Switch to light mode');
        } else {
            // Sun icon
            btn.innerHTML = '☀️';
            btn.setAttribute('aria-label', 'Switch to dark mode');
        }
    });
}
