document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/navbar');
        
        if (!response.ok) {
            if (response.status === 401) {
                window.loadUserProfile();
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const html = await response.text();
        document.getElementById('menu').innerHTML = html;
        
        if (typeof window.loadUserProfile === 'function') {
            await window.loadUserProfile();
        }
    } catch (error) {
        if (error.status === 401 || error.message.includes('token')) {
            window.loadUserProfile();
        } else {
            console.error('Ошибка загрузки навбара:', error);
            document.getElementById('menu').innerHTML = '<div class="alert alert-danger">Ошибка загрузки меню</div>';
        }
    }
});