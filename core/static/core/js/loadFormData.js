document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');
    let measures = []; 
    window.localMeasures = [];
    const actionsTextarea = document.getElementById('actions');

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

    function formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return new Date(date.getTime() - (date.getTimezoneOffset() * 60000 ))
                    .toISOString().slice(0,16).replace('T', ' ');
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
            const category_data =  await loadDataByEvent(event_id, base_data.category_id);
            const savedMeasures = localStorage.getItem('draftMeasures');
            if (savedMeasures) {
                localMeasures = JSON.parse(savedMeasures);
                updateActionsTextarea();
            }

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
            
            const category_data = await response.json();
            return category_data
        } catch (error) {
            handleError(error);
        }
    }

    async function loadMeasures(currentEventId) {
        if (!currentEventId) return;
        
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/measures/by-event/${currentEventId}/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            measures = await response.json();
            updateActionsTextarea();
        } catch (error) {
            console.error('Ошибка загрузки мер:', error);
            alert('Не удалось загрузить принятые меры');
        }
    }

    async function renderInformation(base_data, category_data) {
        document.getElementById('consequences').value = base_data.consequences|| "";
        document.getElementById('loas').value = base_data.loa_id || "";
        document.getElementById('categories').value = base_data.category_id || "";
        document.getElementById('locations').value = base_data.location_id || "";
        document.getElementById('begin').value = formatDateTime(base_data.begin);
        document.getElementById('note').value = base_data.note || "";
        document.getElementById('organization_name').value = base_data.organization_name || "";
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
            document.getElementById('object_id').value = category_data.object_id || "";
            document.getElementById('object').value = category_data.object || "";
            document.getElementById('influenced_objects_id').value = category_data.influenced_objects_id || "";
            document.getElementById('influenced_objects').value = category_data.influenced_objects || "";
            try {
                if (category_data.subsystem_id) {
                    const url = `${window.APP_CONFIG.API_BASE_URL}/api/subsystems/${parseInt(category_data.subsystem_id)}/`;
                    
                    const response = await fetch(url, {
                        headers: { 'Authorization': `Bearer ${accessToken}` }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const subsystem_data = await response.json();
                    document.getElementById('systems').value = subsystem_data.system_id || "";
                    document.getElementById('systems').dispatchEvent(new Event('change'))
                }
            } catch (error) {
                handleError(error); 
            }
            document.getElementById('subsystems').value = category_data.subsystem_id;;
            document.getElementById('subsystem_info').value = category_data.subsystem_info || "";;
            document.getElementById('subsystem_statuses').value = category_data.subsystem_status_id || "";
            document.getElementById('description-equipment-failure').value = category_data.description || "";

            document.getElementById('subsystems').disabled  = true;
            document.getElementById('systems').disabled  = true;
        } else if (base_data.category_id === 2){
            document.getElementById('source-adverse-weathers').value = category_data.source_id || "";
            document.getElementById('precipitations').value = category_data.precipitation_id || "";
            document.getElementById('conditions').value = category_data.condition_id || 1;
            document.getElementById('temperature').value = category_data.temperature || 22 ;
            document.getElementById('input-wind-speed').value = category_data.wind || 0;
            document.getElementById('geography-adverse-weathers').value = category_data.geography || "";
            document.getElementById('description-adverse_weathers').value = category_data.description || "";

            document.getElementById('input-wind-speed').dispatchEvent(new Event('change')) 
        }
        else if (base_data.category_id === 3){
            document.getElementById('source-fire-dangers').value = category_data.source_id || "";
            document.getElementById('area').value = category_data.area || 0;
            document.getElementById('direction').value = category_data.direction || "";
            document.getElementById('description-fire-dangers').value = category_data.description || "";
        }
        else if (base_data.category_id === 4){
            document.getElementById('source-geological-dangers').value = category_data.source_id || "";
            document.getElementById('magnitude').value = category_data.magnitude || 1;
            document.getElementById('magnitudeRange').value = category_data.magnitude || 1;
            document.getElementById('epicenter').value = category_data.epicenter || "";
            document.getElementById('geography-geological-dangers').value = category_data.geography || "";
            document.getElementById('description-geological-dangers').value = category_data.description || "";
        }
        else if (base_data.category_id === 5){
            document.getElementById('source-hydrological-dangers').value = category_data.source_id || "";
            document.getElementById('height').value = category_data.height || 0;
            document.getElementById('water_name').value = category_data.water_name || "";
            document.getElementById('description-hydrological-dangers').value = category_data.description || "";
        }
        else if (base_data.category_id === 6){
            document.getElementById('source-emergency-situations').value = category_data.source_id || "";
            document.getElementById('geography-emergency-situations').value = category_data.geography || "";
            document.getElementById('description-emergency-situations').value = category_data.description || "";
        }
        else if (base_data.category_id === 7){
            document.getElementById('source-other-dangers').value = category_data.source_id || "";
            document.getElementById('description-other-dangers').value = category_data.description || "";
        }
    }

    function updateActionsTextarea() {
        let measuresToShow = [...measures];
        
        // Добавляем локальные меры для новых событий
        if (!getEventIdFromUrl() && window.localMeasures && window.localMeasures.length > 0) {
            measuresToShow = [...window.localMeasures];
        }

        if (measuresToShow.length === 0) {
            actionsTextarea.value = 'Принятые меры отсутствуют';
            return;
        }
        
        const sortedMeasures = measuresToShow.sort(
            (a, b) => new Date(a.adopted_at) - new Date(b.adopted_at)
        );
        
        let text = '';
        sortedMeasures.forEach(measure => {
            const date = formatDateTime(new Date(measure.adopted_at));
            text += `[${date}] ${measure.description}\n\n`;
        });
        
        actionsTextarea.value = text.trim();
        if (!getEventIdFromUrl() && localMeasures.length > 0) {
            localStorage.setItem('draftMeasures', JSON.stringify(localMeasures));
        }
    }
    window.loadMeasures = loadMeasures;
    document.getElementById('begin').value= formatDateTime(new Date());
    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
        loadMeasures(eventId);
    } else {
        console.log('Creating new event');
        
        const actionsTextarea = document.getElementById('actions');
        if (actionsTextarea) {
            actionsTextarea.value = 'Принятые меры отсутствуют';
        }
        
        window.localMeasures = [];
    }
});