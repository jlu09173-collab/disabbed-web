// ============================================
// ABILITYJOBS - MAIN JAVASCRIPT
// Simple HTML/CSS/JS - No React
// ============================================

// ============================================
// 1. APPLY NOW BUTTON HANDLER
// ============================================
function handleApplyNow(jobTitle) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'apply/';

    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCookie('csrftoken');

    const title = document.createElement('input');
    title.type = 'hidden';
    title.name = 'job_title';
    title.value = jobTitle;

    form.appendChild(csrf);
    form.appendChild(title);
    document.body.appendChild(form);
    form.submit();
}

// ============================================
// 2. REGISTRATION HANDLER
// ============================================
function handleRegistration(event) {
    if (event.target && event.target.method && event.target.method.toLowerCase() === 'post') {
        return;
    }
    event.preventDefault();
    
    console.log('🔵 Registration form submitted');
    
    // Get form values
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirmPassword: document.getElementById('confirmPassword').value,
        phone: document.getElementById('phone').value,
        userType: document.getElementById('userType').value,
        disability: document.getElementById('disability').value,
        experience: document.getElementById('experience')?.value || 'Fresher',
        skills: document.getElementById('skills')?.value || ''
    };
    
    console.log('🔵 Form data:', formData);
    
    // Validation
    if (formData.password !== formData.confirmPassword) {
        showToast('Passwords do not match!', 'error');
        return;
    }
    
    if (formData.password.length < 6) {
        showToast('Password must be at least 6 characters!', 'error');
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('userName', formData.name);
    localStorage.setItem('userEmail', formData.email);
    localStorage.setItem('userPhone', formData.phone);
    localStorage.setItem('userType', formData.userType);
    localStorage.setItem('userDisability', formData.disability);
    localStorage.setItem('userExperience', formData.experience);
    localStorage.setItem('userSkills', formData.skills);
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('registrationDate', new Date().toISOString());
    
    // Generate profile code
    const profileCode = generateProfileCode(formData.email);
    localStorage.setItem('profileCode', profileCode);
    
    console.log('🔵 User registered successfully');
    console.log('🔵 Profile code:', profileCode);
    
    showToast('Registration successful! Redirecting to your profile...', 'success');
    
    // Redirect to profile page
    setTimeout(() => {
        window.location.href = 'profile.html';
    }, 1500);
}

// ============================================
// 3. LOGIN HANDLER
// ============================================
function handleLogin(event) {
    if (event.target && event.target.method && event.target.method.toLowerCase() === 'post') {
        return;
    }
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Check if user exists
    const savedEmail = localStorage.getItem('userEmail');
    
    if (email === savedEmail) {
        localStorage.setItem('isLoggedIn', 'true');
        showToast('Login successful!', 'success');
        
        setTimeout(() => {
            window.location.href = 'profile.html';
        }, 1000);
    } else {
        showToast('Invalid credentials! Please register first.', 'error');
    }
}

// ============================================
// 4. LOGOUT HANDLER
// ============================================
function handleLogout() {
    window.location.href = 'logout/';
}

// ============================================
// 5. LOAD USER PROFILE
// ============================================
function loadUserProfile() {
    console.log('🔵 Loading user profile...');
    
    // Check if logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    
    if (!isLoggedIn || isLoggedIn !== 'true') {
        console.log('🔵 User not logged in, redirecting to login...');
        showToast('Please login to view your profile', 'info');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
        return;
    }
    
    // Get user data
    const userData = {
        name: localStorage.getItem('userName') || 'Guest User',
        email: localStorage.getItem('userEmail') || 'guest@example.com',
        phone: localStorage.getItem('userPhone') || 'Not provided',
        userType: localStorage.getItem('userType') || 'Job Seeker',
        disability: localStorage.getItem('userDisability') || 'Not specified',
        experience: localStorage.getItem('userExperience') || 'Fresher',
        skills: localStorage.getItem('userSkills') || 'Not provided',
        profileCode: localStorage.getItem('profileCode') || generateProfileCode(localStorage.getItem('userEmail')),
        registrationDate: localStorage.getItem('registrationDate') || new Date().toISOString()
    };
    
    console.log('🔵 User data loaded:', userData);
    
    // Update DOM elements
    updateElement('profileName', userData.name);
    updateElement('profileName2', userData.name);
    updateElement('profileEmail', userData.email);
    updateElement('profileEmail2', userData.email);
    updateElement('profilePhone', userData.phone);
    updateElement('profileUserType', userData.userType);
    updateElement('profileDisability', userData.disability);
    updateElement('profileExperience', userData.experience);
    updateElement('profileSkills', userData.skills);
    updateElement('profileCode', userData.profileCode);
    updateElement('profileCodeDisplay', userData.profileCode);
    
    // Update profile initial
    updateElement('profileInitial', userData.name.charAt(0).toUpperCase());
    
    // Calculate days since registration
    const regDate = new Date(userData.registrationDate);
    const today = new Date();
    const daysSince = Math.floor((today - regDate) / (1000 * 60 * 60 * 24));
    updateElement('memberSince', `${daysSince} days ago`);
    
    // Generate QR Code
    generateQRCode(userData.profileCode);
    
    // Load applications
    loadApplications();
}

// ============================================
// 6. GENERATE PROFILE CODE
// ============================================
function generateProfileCode(email) {
    // Generate unique 8-character code based on email
    const hash = email.split('').reduce((acc, char) => {
        return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    
    const code = Math.abs(hash).toString(36).toUpperCase().substring(0, 8).padEnd(8, '0');
    return `AJ-${code}`;
}

// ============================================
// 7. GENERATE QR CODE
// ============================================
function generateQRCode(profileCode) {
    const qrContainer = document.getElementById('qrCode');
    if (!qrContainer) return;
    
    // Create QR code URL (using a free QR code API)
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(profileCode)}`;
    
    qrContainer.innerHTML = `
        <img src="${qrUrl}" alt="Profile QR Code" class="w-48 h-48 mx-auto rounded-xl shadow-xl" />
    `;
}

// ============================================
// 8. COPY PROFILE CODE TO CLIPBOARD
// ============================================
function copyProfileCode() {
    const profileCode = localStorage.getItem('profileCode');
    
    if (!profileCode) {
        showToast('No profile code found!', 'error');
        return;
    }
    
    // Copy to clipboard
    navigator.clipboard.writeText(profileCode).then(() => {
        showToast('Profile code copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const input = document.createElement('input');
        input.value = profileCode;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        showToast('Profile code copied!', 'success');
    });
}

// ============================================
// 9. SAVE JOB APPLICATION
// ============================================
function saveJobApplication(jobTitle) {
    let applications = JSON.parse(localStorage.getItem('jobApplications') || '[]');
    
    const newApplication = {
        id: Date.now(),
        jobTitle: jobTitle,
        appliedDate: new Date().toISOString(),
        status: 'Pending'
    };
    
    applications.push(newApplication);
    localStorage.setItem('jobApplications', JSON.stringify(applications));
    
    console.log('🔵 Job application saved:', newApplication);
}

// ============================================
// 10. LOAD APPLICATIONS
// ============================================
function loadApplications() {
    const applicationsContainer = document.getElementById('applicationsContainer');
    if (!applicationsContainer) return;
    
    const applications = JSON.parse(localStorage.getItem('jobApplications') || '[]');
    
    if (applications.length === 0) {
        applicationsContainer.innerHTML = `
            <div class="text-center py-12">
                <p class="text-gray-500 text-lg">No applications yet. Start applying for jobs!</p>
                <a href="jobs.html" class="inline-block mt-4 bg-gradient-to-r from-[#008CA7] to-[#2ECC71] text-white px-8 py-3 rounded-xl font-bold hover:shadow-xl transition-all">
                    Browse Jobs
                </a>
            </div>
        `;
        return;
    }
    
    const html = applications.reverse().map(app => {
        const date = new Date(app.appliedDate);
        const formattedDate = date.toLocaleDateString('en-IN', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        return `
            <div class="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100 hover:border-[#008CA7] transition-all">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <h4 class="text-xl font-bold text-[#222222] mb-2">${app.jobTitle}</h4>
                        <p class="text-sm text-gray-600">Applied on ${formattedDate}</p>
                    </div>
                    <span class="bg-yellow-100 text-yellow-800 px-4 py-1 rounded-full text-sm font-bold">
                        ${app.status}
                    </span>
                </div>
            </div>
        `;
    }).join('');
    
    applicationsContainer.innerHTML = html;
}

// ============================================
// 11. TOAST NOTIFICATION
// ============================================
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existing = document.getElementById('toast');
    if (existing) {
        existing.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'fixed top-6 right-6 z-[9999] px-6 py-4 rounded-xl shadow-2xl text-white font-bold text-lg transform transition-all duration-300 translate-x-0';
    
    // Set color based on type
    if (type === 'success') {
        toast.style.background = 'linear-gradient(135deg, #2ECC71 0%, #27ae60 100%)';
    } else if (type === 'error') {
        toast.style.background = 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)';
    } else {
        toast.style.background = 'linear-gradient(135deg, #008CA7 0%, #006B82 100%)';
    }
    
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="text-white/80 hover:text-white">✕</button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// 12. UPDATE ELEMENT
// ============================================
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

// ============================================
// 13. UPDATE NAVBAR FOR LOGGED IN USER
// ============================================
function updateNavbar() {
    if (document.body.dataset.authenticated === 'true') return;
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const navButtons = document.getElementById('navButtons');
    
    if (!navButtons) return;
    
    if (isLoggedIn === 'true') {
        const userName = localStorage.getItem('userName') || 'User';
        navButtons.innerHTML = `
            <a href="profile.html" class="text-[#222222] hover:text-[#008CA7] font-medium transition-colors">
                👤 ${userName}
            </a>
            <button onclick="handleLogout()" class="bg-gradient-to-r from-[#e74c3c] to-[#c0392b] text-white px-7 py-3 rounded-xl font-bold hover:shadow-2xl transition-all">
                Logout
            </button>
        `;
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

// ============================================
// 14. INITIALIZE ON PAGE LOAD
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔵 AbilityJobs initialized');
    
    // Update navbar
    updateNavbar();
    
    // If on profile page, load profile data
    if (window.location.pathname.includes('profile.html')) {
        loadUserProfile();
    }
    
    // Attach registration form handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
    
    // Attach login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    console.log('🔵 All event handlers attached');
});

// ============================================
// 15. MAKE FUNCTIONS GLOBALLY AVAILABLE
// ============================================
window.handleApplyNow = handleApplyNow;
window.handleLogout = handleLogout;
window.copyProfileCode = copyProfileCode;
window.showToast = showToast;

console.log('✅ AbilityJobs App.js loaded successfully!');
