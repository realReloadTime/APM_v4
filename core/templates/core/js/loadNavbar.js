document.addEventListener('DOMContentLoaded', function() {
    fetch('navbar.html')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById('menu').innerHTML = html;
            loadUserProfile();
        })
        .catch(error => {
            console.error('Ошибка загрузки навбара:', error);
            document.getElementById('menu').innerHTML = '<div class="alert alert-danger">Ошибка загрузки меню</div>';
        });
});