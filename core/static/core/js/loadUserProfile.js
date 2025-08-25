async function refreshAccessToken() {
    try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return;
        }

        const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/refresh_token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (!response.ok) {
            throw new Error('Refresh token failed');
        }

        const data = await response.json();
        
        if (!data.access) {
            throw new Error('Invalid token response');
        }

        localStorage.setItem('access_token', data.access);
        return data.access;
    } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw error; // Прерываем выполнение
    }
}

async function loadUserProfile() {
    try {
        let accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            window.location.href = '/login';
            return;
        }

        const fetchWithTokenRefresh = async (url, options = {}) => {
            try {
                const headers = {
                    ...options.headers,
                    'Authorization': `Bearer ${accessToken}`
                };
                
                let response = await fetch(url, { ...options, headers });
                
                if (response.status === 401) {
                    accessToken = await refreshAccessToken();
                    headers['Authorization'] = `Bearer ${accessToken}`;
                    response = await fetch(url, { ...options, headers });
                    location.reload();
                }
                
                return response;
            } catch (error) {
                if (error.message.includes('token')) {
                    window.location.href = '/login';
                }
                throw error;
            }
        };

        const response = await fetchWithTokenRefresh(
            `${window.APP_CONFIG.API_BASE_URL}/api/users/me/`
        );
        
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.textContent = userData.profile || userData.email || 'Пользователь';
        }
        
        localStorage.setItem('user_permissions', JSON.stringify({
            edit: userData.edit || false,
            read: userData.read || false
        }));

    } catch (error) {
        if (error.message.includes('token')) {
            // Ошибка уже обработана в refreshAccessToken
            return;
        }
        handleError(error);
    }
}

function handleError(error, status = null) {
    console.error('Ошибка:', error);
    
    if (status === 401 || error.message.includes('token')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
}
window.loadUserProfile = loadUserProfile;