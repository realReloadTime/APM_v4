document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const errorContainer = document.getElementById('error-message');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const url = window.APP_CONFIG.API_BASE_URL + '/api/register/';

        if (errorContainer) {
            errorContainer.textContent = '';
            errorContainer.style.display = 'none';
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Ошибка HTTP: ${response.status}`);
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);

            window.location.href = '/table';

        } catch (error) {
            console.error('Ошибка регистрации:', error);
            if (errorContainer) {
                errorContainer.textContent = error.message || 'Ошибка регистрации';
                errorContainer.style.display = 'block';
            }

            document.getElementById('password').value = '';
        }
    });
});