async function refreshAccessToken() {
    try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
            throw new Error('Refresh token not found');
        }

        const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/refresh_token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (!response.ok) {
            throw new Error(`Failed to refresh token: HTTP ${response.status}`);
        }

        const data = await response.json();
        
        if (!data.access) {
            throw new Error('New access token not received');
        }

        localStorage.setItem('access_token', data.access);
        location.reload();
        return data.access;
    } catch (error) {
        console.error('Token refresh failed:', error);
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        throw error; 
    }
}

async function loadUserProfile() {
    try {
        let accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            throw new Error('Токен доступа отсутствует');
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
                }
                
                return response;
            } catch (error) {
                console.error('Request failed:', error);
                throw error;
            }
        };

        const response = await fetchWithTokenRefresh(`${window.APP_CONFIG.API_BASE_URL}/api/users/me/`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
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
        handleError(error);
    }
}

function handleError(error, status = null) {
    console.error('Ошибка:', error);
    
    if (status === 401 || error.message.includes('token')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        setTimeout(() => {
            window.location.href = '/login';
        }, 3000);
    }
    
}