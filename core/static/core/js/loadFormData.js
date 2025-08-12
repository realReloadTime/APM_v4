document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');
    let measures = []; 
    const measuresContainer = document.getElementById('measures-container');
    const saveMeasureBtn = document.getElementById('save-measure');
    const measureDateInput = document.getElementById('measure-date');
    const measureTextInput = document.getElementById('measure-text');
    const measuresModal = new bootstrap.Modal(document.getElementById('measuresModal'));
    const actionsTextarea = document.getElementById('actions');

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
            const category_data =  await loadDataByEvent(event_id, base_data.category_id);

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

    function initMeasures() {
        currentEventId = getEventIdFromUrl();
        if (currentEventId) {
            loadMeasures();
        } else {
            loadLocalMeasures();
        }
        
        setupEventListeners();
        setCurrentDateTime();
    }
    
    function loadLocalMeasures() {
        measures = localMeasures.filter(m => !m.event_id);
        renderMeasures();
    }

    function setCurrentDateTime() {
        const now = new Date();
        const timezoneOffset = now.getTimezoneOffset() * 60000;
        measureDateInput.value = new Date(now - timezoneOffset).toISOString().slice(0, 16);
    }

    function setupEventListeners() {
        // Обработчик сохранения меры
        saveMeasureBtn.addEventListener('click', saveMeasure);
        
        // Сброс формы при закрытии модального окна
        measuresModal._element.addEventListener('hidden.bs.modal', () => {
            measureTextInput.value = '';
            setCurrentDateTime();
        });
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

    async function saveMeasure() {
        const measureData = {
            adopted_at: `${measureDateInput.value}:00Z`,
            description: measureTextInput.value
        };
        
        try {
            if (currentEventId) {
                // Для существующего события - отправляем на сервер
                const url = currentMeasureId 
                    ? `${API_BASE}/api/measures/${currentMeasureId}/update/`
                    : `${API_BASE}/api/measures/`;
                
                const method = currentMeasureId ? 'PUT' : 'POST';
                
                if (!currentMeasureId) {
                    measureData.event_id = currentEventId;
                }
                
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify(measureData)
                });
                
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                const result = await response.json();
                
                // Обновляем список мер
                if (currentMeasureId) {
                    const index = measures.findIndex(m => m.id === currentMeasureId);
                    if (index !== -1) measures[index] = result;
                } else {
                    measures.push(result);
                }
                
            } else {
                // Для нового события - сохраняем локально
                const newMeasure = {
                    ...measureData,
                    id: Date.now(), // Временный ID
                    local: true // Флаг локальной меры
                };
                
                if (currentMeasureId) {
                    // Обновляем существующую локальную меру
                    const index = measures.findIndex(m => m.id === currentMeasureId);
                    if (index !== -1) {
                        measures[index] = newMeasure;
                        // Обновляем в localMeasures
                        const localIndex = localMeasures.findIndex(m => m.id === currentMeasureId);
                        if (localIndex !== -1) localMeasures[localIndex] = newMeasure;
                    }
                } else {
                    // Добавляем новую локальную меру
                    measures.push(newMeasure);
                    localMeasures.push(newMeasure);
                }
                
                saveLocalMeasures();
            }
            
            renderMeasures();
            measuresModal.hide();
            resetMeasureForm();
            
        } catch (error) {
            console.error('Ошибка сохранения меры:', error);
            alert('Не удалось сохранить меру');
        }
    }

    function renderInformation(base_data, category_data) {
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
            document.getElementById('object').value = category_data.object || "";
            document.getElementById('influenced_objects').value = category_data.influenced_objects || "";
            document.getElementById('subsystems').value = category_data.subsystem_id || "";
            document.getElementById('systems').value = category_data.system_id || "" ;
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
        if (measures.length === 0) {
            actionsTextarea.value = 'Принятые меры отсутствуют';
            return;
        }
        
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

    // Обновленная функция удаления меры
    async function deleteCurrentMeasure() {
        if (!currentMeasureId) return;
        
        if (!confirm('Вы уверены, что хотите удалить эту меру?')) return;
        
        try {
            if (currentEventId) {
                // Удаляем меру с сервера
                const response = await fetch(
                    `${API_BASE}/api/measures/${currentMeasureId}/`,
                    {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${accessToken}` }
                    }
                );
                
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                // Удаляем из списка
                measures = measures.filter(m => m.id !== currentMeasureId);
            } else {
                // Удаляем локальную меру
                measures = measures.filter(m => m.id !== currentMeasureId);
                localMeasures = localMeasures.filter(m => m.id !== currentMeasureId);
                saveLocalMeasures();
            }
            
            renderMeasures();
            measuresModal.hide();
            resetMeasureForm();
            
        } catch (error) {
            console.error('Ошибка удаления меры:', error);
            alert('Не удалось удалить меру');
        }
    }
    
    // Функция отправки всех локальных мер при создании события
    async function sendLocalMeasures(eventId) {
        try {
            for (const measure of localMeasures.filter(m => !m.event_id)) {
                const response = await fetch(`${API_BASE}/api/measures/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        ...measure,
                        event_id: eventId
                    })
                });
                
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Очищаем отправленные локальные меры
            localMeasures = localMeasures.filter(m => m.event_id);
            saveLocalMeasures();
            
        } catch (error) {
            console.error('Ошибка отправки локальных мер:', error);
            throw error; // Пробрасываем ошибку для обработки в sendData
        }
    }

    function renderMeasures() {
        measuresContainer.innerHTML = '';
        
        if (measures.length === 0) {
            measuresContainer.innerHTML = '<div class="text-center p-3 text-muted">Принятые меры отсутствуют</div>';
            return;
        }
        
        // Сортируем меры по дате (новые сверху)
        const sortedMeasures = [...measures].sort(
            (a, b) => new Date(b.adopted_at) - new Date(a.adopted_at)
        );
        
        sortedMeasures.forEach(measure => {
            const measureElement = document.createElement('div');
            measureElement.className = `card mb-2 measure-item ${measure.local ? 'local-measure' : ''}`;
            measureElement.dataset.id = measure.id;
            
            const date = new Date(measure.adopted_at).toLocaleString('ru-RU');
            
            measureElement.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h6 class="card-title">${date} ${measure.local ? '(локально)' : ''}</h6>
                        <button class="btn btn-sm btn-outline-secondary edit-measure">
                            <i class="bi bi-pencil"></i>
                        </button>
                    </div>
                    <p class="card-text">${measure.description}</p>
                </div>
            `;
            
            // Обработчики событий
            measureElement.addEventListener('dblclick', () => {
                openMeasureModalForEdit(measure.id);
            });
            
            measureElement.querySelector('.edit-measure').addEventListener('click', (e) => {
                e.stopPropagation();
                openMeasureModalForEdit(measure.id);
            });
            
            measuresContainer.appendChild(measureElement);
        });
    }
    

    initMeasures();
    const eventId = getEventIdFromUrl();
    if (eventId) {
        loadData(eventId);
        loadMeasures(currentEventId);
    } else {
        console.log('Event ID not found in URL');
    }
});