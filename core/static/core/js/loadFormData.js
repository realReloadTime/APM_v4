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
            
            const base_data = await response.json();
            const category_data = loadDataByEvent(event_id, base_data.category_id);

            renderInformation(base_data, category_data);

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
            
            const data = await response.json();

        return data

        } catch (error) {
            handleError(error);
        }
    }

    function renderInformation(base_data, category_data) {
        if (base_data.category_id === 1) {
            
        }
        document.getElementById('consequences').value = base_data.consequences || '';
        document.getElementById('loas').value = base_data.loa || '';
    }


    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
    } else {
        console.error('Event ID not found in URL');
        alert('Не указан идентификатор события в URL');
    }
});