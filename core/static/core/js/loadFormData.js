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

    function formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toISOString().split('T')[0]
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
        document.getElementById('consequences').value = base_data.consequences;
        document.getElementById('loas').value = base_data.loa_id;
        document.getElementById('categories').value = base_data.category_id;
        document.getElementById('locations').value = base_data.location_id;
        document.getElementById('begin').value = formatDateTime(base_data.begin);
        document.getElementById('note').value = base_data.note;
        document.getElementById('organization_name').value = base_data.organization_name;
        document.getElementById('personnel_count').value = base_data.personnel_count;
        document.getElementById('technic_count').value = base_data.technic_count;

        if (base_data.end != null){
            document.getElementById('end').value = formatDateTime(base_data.end);
            document.getElementById('is_ended').checked = true;
            document.getElementById('is_ended').dispatchEvent(new Event('change')) // для появления блока с концом даты

            document.getElementById('end').disabled  = true;
            document.getElementById('is_ended').disabled  = true;
        }
        
        document.getElementById('categories').dispatchEvent(new Event('change')) // так вызывается смена блока

        document.getElementById('begin').disabled = true;
        document.getElementById('loas').disabled  = true;
        document.getElementById('locations').disabled  = true;
        document.getElementById('categories').disabled  = true;
        if (base_data.category_id === 1) {
            document.getElementById('object').value = category_data.object;
            
        }
        
    }


    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
    } else {
        console.log('Event ID not found in URL');
    }
});