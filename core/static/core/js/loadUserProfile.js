function handleError(error, status = null) {
    console.error('Ошибка:', error);
    
    if (status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setTimeout(() => window.location.href = '/login', 3000);
    }
    
    console.error('Ошибка загрузки профиля:', error);
    
    const usernameElement = document.getElementById('username');
    if (usernameElement) {
        usernameElement.textContent = 'Гость';
        usernameElement.classList.add('text-muted');
    }
}

async function loadUserProfile() {
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
        handleError(new Error('Токен доступа отсутствует'), 401);
        return;
    }

    try {
        const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/users/me/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        const status = response.status;
        
        if (!response.ok) {
            throw { error: new Error(`HTTP error! status: ${status}`), status };
        }

        const userData = await response.json();
        
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.textContent = userData.name || userData.email || 'Пользователь';
        }
        
        localStorage.setItem('user_permissions', JSON.stringify({
            edit: userData.edit || false,
            read: userData.read || false
        }));

    } catch (error) {
        const status = error.status || (error.response && error.response.status);
        handleError(error.error || error, status);
    }
}