document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');
    const userEmailElement = document.getElementById('username');
    const eventsTableBody = document.getElementById('eventsTableBody');
    const errorContainer = document.getElementById('error-message');

    // if (!accessToken) {
    //     window.location.href = '/login.html';
    //     return;
    // }

    // function handleError(error, status) {
    // console.error('Ошибка:', error);
    //     if (status === 401) {
    //         errorContainer.textContent = 'Сессия истекла. Пожалуйста, войдите снова.';
    //         localStorage.removeItem('access_token');
    //         localStorage.removeItem('refresh_token');
    //         setTimeout(() => window.location.href = '/login.html', 3000);
    //     } else {
    //         errorContainer.textContent = error.message || `Ошибка ${status}`;
    //     }
    //     errorContainer.style.display = 'block';
    // }

    async function loadUserProfile() {
        try {
            const response = await fetch('${window.APP_CONFIG.API_BASE_URL}/api/users/me/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const userData = await response.json();
            userEmailElement.textContent = userData.email;

            localStorage.setItem('user_permissions', JSON.stringify({
                edit: userData.edit,
                read: userData.read
            }));

        } catch (error) {
            handleError(error, error.status);
        }
    }

    async function loadEvents() {
        try {
            const response = await fetch('${window.APP_CONFIG.API_BASE_URL}/api/events/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const events = await response.json();
            renderEventsTable(events);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    function renderEventsTable(events) {
        eventsTableBody.innerHTML = '';

        if (events.length === 0) {
            eventsTableBody.innerHTML = `
                        <tr>
                            <td colspan="8" class="text-center">Нет доступных событий</td>
                        </tr>
                    `;
            return;
        }

        events.forEach(event => {
            const beginDate = new Date(event.begin).toLocaleString('ru-RU');
            const endDate = event.end ? new Date(event.end).toLocaleString('ru-RU') : '-';
            const hasAttachments = event.attachments.length > 0 ? 'Да' : 'Нет';

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${beginDate}</td>
                        <td>${event.loa}</td>
                        <td>${event.category}</td>
                        <td>${event.location}</td>
                        <td>${event.note}</td>
                        <td>${endDate}</td>
                        <td>${hasAttachments}</td>
                        <td>
                            <input type="checkbox" class="form-check"  id="{{event.id}}" checked>
                        </td>
                    `;
                    eventsTableBody.appendChild(row);
                });

                document.querySelectorAll('.view-event').forEach(button => {
                    button.addEventListener('click', function() {
                        const eventId = this.getAttribute('data-id');
                        window.location.href = `event-details.html?id=${eventId}`;
                    });
                });
            }

            loadUserProfile();
            loadEvents();
        });