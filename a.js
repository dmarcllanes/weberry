// State management
const state = {
    currentStep: 1,
    totalSteps: 4,
    formData: {
        siteName: '',
        siteTagline: '',
        bio: '',
        cta: '',
        email: '',
        instagram: '',
        linkedin: '',
        imageUrl: null
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateProgress();
});

// Setup Event Listeners
function setupEventListeners() {
    // File upload handling
    const fileUpload = document.getElementById('logo');
    fileUpload?.parentElement?.addEventListener('click', () => fileUpload.click());
    
    // Drag and drop for file upload
    const uploadArea = document.querySelector('.file-upload');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleDrop);
    }
}

// Navigation
function nextStep(event) {
    if (event) {
        event.preventDefault();
    }
    
    // Validate current step
    if (!validateCurrentStep()) {
        return;
    }
    
    // Save form data
    saveFormData();
    
    // Move to next step
    if (state.currentStep < state.totalSteps) {
        state.currentStep++;
    } else {
        showSuccess();
        return;
    }
    
    updateUI();
}

function prevStep() {
    if (state.currentStep > 1) {
        saveFormData();
        state.currentStep--;
        updateUI();
    }
}

// Update UI
function updateUI() {
    // Hide all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.add('hidden');
    });
    
    // Show current step
    const currentStepElement = document.getElementById(`step${state.currentStep}`);
    if (currentStepElement) {
        currentStepElement.classList.remove('hidden');
    }
    
    updateProgress();
    updatePreview();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Update progress bar and label
function updateProgress() {
    const progressFill = document.getElementById('progressFill');
    const stepLabel = document.getElementById('stepLabel');
    
    const progress = (state.currentStep / state.totalSteps) * 100;
    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
    
    if (stepLabel) {
        stepLabel.textContent = `Step ${state.currentStep} of ${state.totalSteps}`;
    }
}

// Save form data
function saveFormData() {
    state.formData.siteName = document.getElementById('siteName')?.value || '';
    state.formData.siteTagline = document.getElementById('siteTagline')?.value || '';
    state.formData.bio = document.getElementById('bio')?.value || '';
    state.formData.cta = document.getElementById('cta')?.value || '';
    state.formData.email = document.getElementById('email')?.value || '';
    state.formData.instagram = document.getElementById('instagram')?.value || '';
    state.formData.linkedin = document.getElementById('linkedin')?.value || '';
}

// Validate current step
function validateCurrentStep() {
    if (state.currentStep === 2) {
        const siteName = document.getElementById('siteName')?.value.trim();
        if (!siteName) {
            showError('Please enter your name or business name');
            return false;
        }
    }
    
    if (state.currentStep === 4) {
        const email = document.getElementById('email')?.value.trim();
        if (!email || !isValidEmail(email)) {
            showError('Please enter a valid email address');
            return false;
        }
    }
    
    return true;
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show error message
function showError(message) {
    alert(message); // Simple alert - can be replaced with toast notification
}

// Update preview
function updatePreview() {
    const previewContent = document.getElementById('previewContent');
    if (!previewContent) return;
    
    const { siteName, siteTagline, bio, cta, email, instagram, linkedin, imageUrl } = state.formData;
    
    // Only show preview if we have some data
    if (!siteName && !siteTagline && !bio) {
        previewContent.innerHTML = `
            <div class="preview-placeholder">
                <p>Your site preview will appear here</p>
            </div>
        `;
        return;
    }
    
    let previewHTML = '<div class="preview-site">';
    
    // Profile image or placeholder
    if (imageUrl) {
        previewHTML += `<img src="${imageUrl}" alt="${siteName}" class="preview-image" style="object-fit: cover; height: 200px;" />`;
    } else {
        previewHTML += `<div class="preview-image">👤</div>`;
    }
    
    // Name
    if (siteName) {
        previewHTML += `<div class="preview-name">${escapeHtml(siteName)}</div>`;
    }
    
    // Tagline
    if (siteTagline) {
        previewHTML += `<div class="preview-tagline">${escapeHtml(siteTagline)}</div>`;
    }
    
    // Bio
    if (bio) {
        previewHTML += `<div class="preview-bio">${escapeHtml(bio)}</div>`;
    }
    
    // CTA Button
    if (cta) {
        previewHTML += `<div class="preview-cta">${escapeHtml(cta)}</div>`;
    }
    
    // Contact section
    if (email || instagram || linkedin) {
        previewHTML += '<div class="preview-contact">';
        
        if (email) {
            previewHTML += `<div class="preview-email">📧 ${escapeHtml(email)}</div>`;
        }
        
        if (instagram || linkedin) {
            let socialLinks = '';
            if (instagram) {
                socialLinks += `<a href="${escapeHtml(instagram)}" target="_blank" style="margin-right: 8px; text-decoration: none; color: #4F46E5;">Instagram</a>`;
            }
            if (linkedin) {
                socialLinks += `<a href="${escapeHtml(linkedin)}" target="_blank" style="text-decoration: none; color: #4F46E5;">LinkedIn</a>`;
            }
            previewHTML += `<div style="font-size: 0.85rem;">${socialLinks}</div>`;
        }
        
        previewHTML += '</div>';
    }
    
    previewHTML += '</div>';
    previewContent.innerHTML = previewHTML;
}

// Handle image upload
function handleImageUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Validate file type
    if (!['image/png', 'image/jpeg'].includes(file.type)) {
        showError('Please upload a PNG or JPEG image');
        return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('Image must be smaller than 5MB');
        return;
    }
    
    // Read file
    const reader = new FileReader();
    reader.onload = (e) => {
        state.formData.imageUrl = e.target?.result;
        updatePreview();
    };
    reader.readAsDataURL(file);
}

// Handle drag and drop
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = 'rgba(79, 70, 229, 0.05)';
    e.currentTarget.style.borderColor = '#4F46E5';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';
    e.currentTarget.style.borderColor = '';
    
    const file = e.dataTransfer?.files?.[0];
    if (file) {
        const input = document.getElementById('logo');
        if (input) {
            input.files = e.dataTransfer.files;
            handleImageUpload({ target: input });
        }
    }
}

// Publish site
function publishSite(event) {
    event.preventDefault();
    saveFormData();
    
    if (!validateCurrentStep()) {
        return;
    }
    
    showSuccess();
}

// Show success screen
function showSuccess() {
    // Hide all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.add('hidden');
    });
    
    // Show success screen
    const successScreen = document.getElementById('stepSuccess');
    if (successScreen) {
        successScreen.classList.remove('hidden');
    }
    
    // Update progress to 100%
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        progressFill.style.width = '100%';
    }
    
    // Generate site link
    const siteName = state.formData.siteName?.toLowerCase().replace(/\s+/g, '-') || 'yourname';
    const siteLink = document.getElementById('siteLink');
    if (siteLink) {
        siteLink.textContent = `https://presence.app/${siteName}`;
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Copy site link to clipboard
function copySiteLink() {
    const siteLink = document.getElementById('siteLink');
    if (!siteLink) return;
    
    const text = siteLink.textContent;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Link copied to clipboard!');
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Link copied to clipboard!');
    }
}

// Show notification
function showNotification(message) {
    // Simple notification - can be replaced with toast
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #10B981;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        font-weight: 600;
        animation: slideIn 0.3s ease-in-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Reset flow
function resetFlow() {
    state.currentStep = 1;
    state.formData = {
        siteName: '',
        siteTagline: '',
        bio: '',
        cta: '',
        email: '',
        instagram: '',
        linkedin: '',
        imageUrl: null
    };
    
    // Clear all form inputs
    document.querySelectorAll('input[type="text"], input[type="email"], textarea').forEach(input => {
        input.value = '';
    });
    document.getElementById('logo').value = '';
    
    updateUI();
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
