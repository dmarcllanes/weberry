// Okenaba - Client-side step navigation and utilities

document.addEventListener('DOMContentLoaded', function() {
    updateProgress();
    updatePreview();
});

// --- Step Navigation ---

var currentStep = 1;
var totalSteps = 4;

function nextStep(event) {
    if (event) event.preventDefault();
    if (!validateCurrentStep()) return;

    if (currentStep < totalSteps) {
        currentStep++;
        updateUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateUI();
    }
}

function goToStep(step) {
    if (step >= 1 && step <= totalSteps) {
        currentStep = step;
        updateUI();
    }
}

function updateUI() {
    var steps = document.querySelectorAll('.step');
    steps.forEach(function(step) {
        step.classList.add('hidden');
    });

    var current = document.getElementById('step' + currentStep);
    if (current) current.classList.remove('hidden');

    updateProgress();
    updatePreview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgress() {
    var progressFill = document.getElementById('progressFill');
    var stepLabel = document.getElementById('stepLabel');

    if (progressFill) {
        var pct = (currentStep / totalSteps) * 100;
        progressFill.style.width = pct + '%';
    }
    if (stepLabel) {
        stepLabel.textContent = 'Step ' + currentStep + ' of ' + totalSteps;
    }
}

// --- Validation ---

function validateCurrentStep() {
    if (currentStep === 2) {
        var name = document.getElementById('business_name');
        if (name && !name.value.trim()) {
            showError('Please enter your business name');
            name.focus();
            return false;
        }
        var type = document.getElementById('website_type');
        if (type && !type.value) {
            showError('Please select a website type');
            type.focus();
            return false;
        }
    }
    if (currentStep === 3) {
        var goal = document.getElementById('primary_goal');
        if (goal && !goal.value) {
            showError('Please select a primary goal');
            goal.focus();
            return false;
        }
    }
    return true;
}

function validateBeforeSubmit() {
    // Run validation for current step before form submit
    // Steps 1-3 validated by nextStep; step 4 validated here
    var name = document.getElementById('business_name');
    if (name && !name.value.trim()) {
        showError('Business name is required');
        goToStep(2);
        name.focus();
        return false;
    }
    var type = document.getElementById('website_type');
    if (type && !type.value) {
        showError('Website type is required');
        goToStep(2);
        type.focus();
        return false;
    }
    var goal = document.getElementById('primary_goal');
    if (goal && !goal.value) {
        showError('Primary goal is required');
        goToStep(3);
        goal.focus();
        return false;
    }
    return true;
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
        previewContent.innerHTML = '<div class="preview-placeholder"><p>Your site preview will appear here</p></div>';
        return;
    }

    var html = '<div class="preview-site">';
    html += '<div class="preview-image">' + escapeHtml(nameVal ? nameVal.charAt(0).toUpperCase() : '?') + '</div>';
    if (nameVal) html += '<div class="preview-name">' + escapeHtml(nameVal) + '</div>';
    if (taglineVal) html += '<div class="preview-tagline">' + escapeHtml(taglineVal) + '</div>';
    if (descVal) html += '<div class="preview-bio">' + escapeHtml(descVal) + '</div>';
    if (emailVal) {
        html += '<div class="preview-contact"><div class="preview-email">' + escapeHtml(emailVal) + '</div></div>';
    }
    html += '</div>';
    previewContent.innerHTML = html;
}

// --- Clipboard ---

function copySiteLink(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function() {
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
    setTimeout(function() {
        el.style.opacity = '0';
        setTimeout(function() { el.remove(); }, 300);
    }, 2500);
}

// --- Utilities ---

function escapeHtml(text) {
    var map = {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
