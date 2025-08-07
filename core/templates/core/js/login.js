document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const url = 'https://pameax-5-136-82-129.ru.tuna.am/api/login/';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Sec-Fetch-Site': 'cross-site',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                }),
                credentials: 'include',
                mode: 'cors' 
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok' + response.status);
                }
                return response.json();
            })
            .then(data => {
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('access_token', data.access);
                
                console.log('Токены сохранены:', data);
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        });
    });