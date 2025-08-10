document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorContainer = document.getElementById('error-message'); // Добавьте этот элемент в вашу HTML-разметку

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const url = `${window.APP_CONFIG.API_BASE_URL}/api/login/`;

        if (errorContainer) {
            errorContainer.textContent = '';
            errorContainer.style.display = 'none';
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Ошибка HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            console.log('Успешная авторизация. Токены сохранены');

            window.location.href = '/table';

        } catch (error) {
            console.error('Ошибка авторизации:', error);
            if (errorContainer) {
                errorContainer.textContent = error.message || 'Неверный email или пароль';
                errorContainer.style.display = 'block';
            }
            
            document.getElementById('password').value = '';
        }
    });
});