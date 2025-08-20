document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');

    function handleError(error, status) {
        console.error('Ошибка:', error);
        if (status === 401 || error.message.includes('token')) {
            window.loadUserProfile();
        }
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
            categoryData = await loadDataByEvent(event_id, data.category_id)
            renderInformation(data, categoryData);

        } catch (error) {
            handleError(error);
        }
    }

    async function loadDataByEvent(event_id, category_id) {
        try {
            const categories = [
            { key: 1, label: 'equipment_failures' },
            { key: 2, label: 'adverse_weathers' },
            { key: 3, label: 'fire_dangers' },
            { key: 4, label: 'geological_dangers' },
            { key: 5, label: 'hydrological_dangers' },
            { key: 6, label: 'emergency_situations' },
            { key: 7, label: 'other_dangers' }
        ];
        const category = categories.find(cat => cat.key === category_id);
        const url = `${window.APP_CONFIG.API_BASE_URL}/api/${category.label}/by-event/${event_id}/`;
            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            const category_data = await response.json();
            return category_data
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

    function renderInformation(data, categoryData) {
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
            { key: 'object', label: 'Объект' },
            { key: 'influenced_objects', label: 'Затронутые объекты' },
            { key: 'system', label: 'Система сбоя' },
            { key: 'subsystem', label: 'Тип оборудования' },
            { key: 'subsystem_info', label: 'Уточнение по оборудованию' },
            { key: 'subsystem_status', label: 'Статус оборудования' },
            { key: 'geography', label: 'Географическая территория' },
            { key: 'source', label: 'Источник' },
            { key: 'precipitation', label: 'Осадки' },
            { key: 'condition', label: 'Метеорологические условия' },
            { key: 'temperature', label: 'Температура' },
            { key: 'wind', label: 'Скорость ветра' },
            { key: 'direction', label: 'Направление пожара' },
            { key: 'area', label: 'Площадь пожара' },
            { key: 'magnitude', label: 'Магнитуда' },
            { key: 'epicenter', label: 'Эпицентр' },
            { key: 'water_name', label: 'Название водоема' },
            { key: 'height', label: 'Уровень воды' },
            { key: 'description', label: 'Описание' },
        ];

        tableFields.forEach(item => {
            if (categoryData[item.key] !== undefined && categoryData[item.key] !== null) {
                const row = document.createElement('tr');
                
                const headerCell = document.createElement('th');
                headerCell.scope = 'row';
                headerCell.textContent = item.label;
                
                const dataCell = document.createElement('td');
                
                if (item.key === 'begin' || item.key === 'end') {
                    const date = new Date(categoryData[item.key]);
                    dataCell.textContent = date.toLocaleString('ru-RU');
                } else {
                    dataCell.textContent = categoryData[item.key];
                }
                
                row.appendChild(headerCell);
                row.appendChild(dataCell);
                tbody.appendChild(row);
            }
            else if (data[item.key] !== undefined && data[item.key] !== null) {
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

    async function deleteEvent(eventId) {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/events/${eventId}/delete/`, {
                method: 'DELETE',
                headers: { 
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            alert('Событие успешно удалено!');
            window.location.href = '/table'; // Перенаправляем на страницу таблицы
        } catch (error) {
            handleError(error);
        }
    }

    function setupDeleteConfirmation(eventId) {
        const deleteButton = document.getElementById('deleteButton');
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        
        if (deleteButton && confirmDeleteBtn) {
            deleteButton.addEventListener('click', function() {
                const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
                confirmDeleteModal.show();
            });
            
            confirmDeleteBtn.addEventListener('click', function() {
                deleteEvent(eventId);
            });
        }
    }

    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
        loadMeasures(eventId);
        changeRef(eventId);
        setupDeleteConfirmation(eventId);
    } else {
        console.error('Event ID not found in URL');
        alert('Не указан идентификатор события в URL');
    }
});