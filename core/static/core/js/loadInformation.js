document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');

    function handleError(error, status) {
        console.error('Ошибка:', error);
        alert(`Произошла ошибка: ${error.message || status || 'Неизвестная ошибка'}`);
    }

    function getEventIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('event_id');
    }

    async function loadData(event_id) {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/events/${event_id}/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            const data = await response.json();
            renderInformation(data);

        } catch (error) {
            handleError(error);
        }
    }
    async function loadMeasures(eventId) {
    try {
        const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/measures/by-event/${eventId}/`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        measures = await response.json();
        renderMeasures(measures);
    } catch (error) {
        console.error('Ошибка загрузки мер:', error);
        alert('Не удалось загрузить принятые меры');
    }
}
    function renderMeasures(measures) {
        actionsTextarea = document.getElementById('actions')
         const sortedMeasures = [...measures].sort(
            (a, b) => new Date(a.adopted_at) - new Date(b.adopted_at)
        );
        
        let text = '';
        sortedMeasures.forEach(measure => {
            const date = new Date(measure.adopted_at).toLocaleString('ru-RU');
            text += `[${date}] ${measure.description}\n\n`;
        });
        
        actionsTextarea.value = text.trim();
    }

    function renderInformation(data) {
        document.getElementById('consequences').value = data.consequences || '';
        document.getElementById('created_by').value = data.created_by || '';

        const tbody = document.querySelector('.table tbody');
        tbody.innerHTML = '';

        const tableFields = [
            { key: 'begin', label: 'Начало события' },
            { key: 'loa', label: 'Филиал' },
            { key: 'category', label: 'Категория' },
            { key: 'location', label: 'Место' },
            { key: 'personnel_count', label: 'Количество персонала' },
            { key: 'technic_count', label: 'Количество техники' },
            { key: 'organization_name', label: 'Организация' },
            { key: 'note', label: 'Примечание' },
            { key: 'end', label: 'Окончание события' }
        ];

        tableFields.forEach(item => {
            if (data[item.key] !== undefined && data[item.key] !== null) {
                const row = document.createElement('tr');
                
                const headerCell = document.createElement('th');
                headerCell.scope = 'row';
                headerCell.textContent = item.label;
                
                const dataCell = document.createElement('td');
                
                if (item.key === 'begin' || item.key === 'end') {
                    const date = new Date(data[item.key]);
                    dataCell.textContent = date.toLocaleString('ru-RU');
                } else {
                    dataCell.textContent = data[item.key];
                }
                
                row.appendChild(headerCell);
                row.appendChild(dataCell);
                tbody.appendChild(row);
            }
        });
    }

    function changeRef(eventId) {
        if (eventId) {
            document.getElementById('editButtonLink').href = `/form/?event_id=${eventId}`;
        } else {
            console.error('Event ID not found in URL');
            alert('Не указан идентификатор события');
        }
    }

    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
        loadMeasures(eventId);
        changeRef(eventId)
    } else {
        console.error('Event ID not found in URL');
        alert('Не указан идентификатор события в URL');
    }
});