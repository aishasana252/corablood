document.addEventListener("DOMContentLoaded", function () {
    // 1. For Login Page: Convert Lock Icon to Eye Icon Toggle
    // The login page password field might not have an ID, so we select by name
    var passwordInput = document.querySelector('input[name="password"]');
    if (passwordInput && document.body.classList.contains('login-page')) {
        // Find the lock icon next to it
        var lockIcon = passwordInput.parentElement.querySelector('.fa-lock');
        if (lockIcon) {
            // Change it to eye initially
            lockIcon.className = 'fas fa-eye';
            lockIcon.style.cursor = 'pointer';
            
            // Allow clicking to toggle
            lockIcon.parentElement.addEventListener('click', function() {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    lockIcon.className = 'fas fa-eye-slash';
                } else {
                    passwordInput.type = 'password';
                    lockIcon.className = 'fas fa-eye';
                }
            });
        }
    }

    // 2. For User Creation/Change Forms: Add Eye Icon to password fields
    var passwordFields = document.querySelectorAll('.form-group input[type="password"]');
    passwordFields.forEach(function (field) {
        // If it's already an input group (like login), skip it
        if (field.parentElement.classList.contains('input-group')) return;

        field.parentElement.style.position = 'relative';

        var toggleIcon = document.createElement('i');
        toggleIcon.className = 'fas fa-eye';
        toggleIcon.style.position = 'absolute';
        toggleIcon.style.right = '10px';
        toggleIcon.style.top = '50%';
        toggleIcon.style.transform = 'translateY(-50%)';
        toggleIcon.style.cursor = 'pointer';
        toggleIcon.style.color = '#6c757d';
        toggleIcon.style.zIndex = '10';

        field.parentElement.appendChild(toggleIcon);
        field.style.paddingRight = '35px';

        toggleIcon.addEventListener('click', function () {
            if (field.type === 'password') {
                field.type = 'text';
                toggleIcon.className = 'fas fa-eye-slash';
            } else {
                field.type = 'password';
                toggleIcon.className = 'fas fa-eye';
            }
        });
    });
});

