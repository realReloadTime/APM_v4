document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('save');
    const accessToken = localStorage.getItem('access_token');
    const validationRules = {
        loa_id: {required: true,},
        category_id: {required: true,},
        location_id: {required: true,},
        begin: {
            required: true,
            isDate: true,
            message: 'Укажите корректную дату начала'
        },
        consequences: {
            required: true,
            minLength: 10,
            message: 'Опишите последствия (минимум 10 символов)'
        },
        personnel_count: {
            isNumber: true,
            min: 0,
            message: 'Укажите число ≥ 0'
        },
        technic_count: {
            isNumber: true,
            min: 0,
            message: 'Укажите число ≥ 0'
        },
        organization_name: {},
        note: {
            required: true,
            minLength: 10,
            message: 'Опишите примечание (минимум 10 символов)'
        },
        end:{},
        description:{
            required: true,
            minLength: 10,
            message: 'Опишите событие (минимум 10 символов)'
        },
        area:{
            required: true,
            message: 'Укажите площадь пожара'
        },
        object_id:{
            required: true,
            message: 'Выберите обьект'
        },
        influenced_objects_id:{ },
        subsystem_info:{ },
        subsystem_id:{
            required: true,
            message: 'Укажите тип оборудования'
        },
        system_id:{
            required: true,
            message: 'Укажите систему'
        },
        subsystem_status_id:{
            required: true,
            message: 'Укажите состояние оборудования'
        },
        precipitation_id:{
            required: true,
            message: 'Укажите осадки'
        },
        source_id:{
            required: true,
            message: 'Укажите источник'
        },
        condition_id:{
            required: true,
            message: 'Укажите метеоусловия'
        },
        wind:{
            required: true,
            message: 'Укажите скорость ветра'
        },
        temperature:{
            required: true,
            min: -273,
            message: 'Укажите температуру'
        },
        direction:{
            required: true,
            message: 'Укажите направление',
            minLength: 2,
        },
        geography:{
            required: true,
            minLength: 5,
            message: 'Укажите место проишествия'
        },
        epicenter:{
            required: true,
            minLength: 5,
            message: 'Укажите эпицентр события'
        },
        magnitude: {
            isNumber: true,
            min: 0,
            message: 'Укажите число ≥ 0'
        }, 
        water_name: {
            required: true,
            message: 'Укажите название водоема'
        }, 
        height: {
            isNumber: true,
            min: 0,
            message: 'Укажите ожидаемый уровень воды'
        },

    };

    const categories = [
            { key: 1, label: 'equipment_failures' },
            { key: 2, label: 'adverse_weathers' },
            { key: 3, label: 'fire_dangers' },
            { key: 4, label: 'geological_dangers' },
            { key: 5, label: 'hydrological_dangers' },
            { key: 6, label: 'emergency_situations' },
            { key: 7, label: 'other_dangers' } 
    ];

    function validateField(fieldId, value) {
        const rules = validationRules[fieldId];
        if (!rules) return true; 
        
        if (rules.required && !value) {
            return rules.message;
        }
        
        if (rules.minLength && value.length < rules.minLength) {
            return rules.message;
        }
        
        if (rules.isNumber && isNaN(Number(value))) {
            return rules.message;
        }
        
        if (rules.min !== undefined && Number(value) < rules.min) {
            return rules.message;
        }
        
        return ;
    }

    function markFieldAsInvalid(fieldId, message) {
        
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        field.classList.add('is-invalid');
        
        let errorElement = field.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        }

    function markFieldAsValid(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        field.classList.remove('is-invalid');
        
        const errorElement = field.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.remove();
        }
    }

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
        return date.toISOString();
    }

    async function sendData(eventID) {
    try {
        const base_data = {
            loa_id: document.getElementById('loas').value,
            category_id: document.getElementById('categories').value,
            location_id: document.getElementById('locations').value,
            begin: formatDateTime(document.getElementById('begin').value),
            consequences: document.getElementById('consequences').value,
            note: document.getElementById('note').value,
            organization_name: document.getElementById('organization_name').value,
            personnel_count: parseInt(document.getElementById('personnel_count').value),
            technic_count: parseInt(document.getElementById('technic_count').value)
        };

        if (document.getElementById('is_ended').checked) {
            base_data.end = formatDateTime(document.getElementById('end').value);
        }
        
        const errors = {};
        let isValid = true;
        
        for (const [fieldId, value] of Object.entries(base_data)) {
            const error = validateField(fieldId, value);
            if (error) {
                errors[fieldId] = error;
                isValid = false;
                markFieldAsInvalid(fieldId, error);
            } else {
                markFieldAsValid(fieldId);
            }
        }
        let category_data = {}
        switch (parseInt(base_data.category_id)) {
            case 1: 
                category_data = {
                    object_id: document.getElementById('object_id').value,
                    influenced_objects_id: (document.getElementById('influenced_objects_id').value).split(','),
                    subsystem_id: document.getElementById('subsystems').value,
                    subsystem_status_id: document.getElementById('subsystem_statuses').value,
                    description: document.getElementById('description-equipment-failure').value,
                    subsystem_info: document.getElementById('subsystem_info').value,
                }
                break;
            case 2:
                category_data = {
                    source_id: document.getElementById('source-adverse-weathers').value,
                    precipitation_id: document.getElementById('precipitations').value,
                    condition_id: document.getElementById('conditions').value,
                    temperature: document.getElementById('temperature').value,
                    wind: document.getElementById('input-wind-speed').value,
                    geography: document.getElementById('geography-adverse-weathers').value,
                    description: document.getElementById('description-adverse_weathers').value
                }
                break;
            case 3:
                category_data = {
                    source_id: document.getElementById('source-fire-dangers').value,
                    area: document.getElementById('area').value,
                    direction: document.getElementById('direction').value,
                    description: document.getElementById('description-fire-dangers').value,
                }
                break;
            case 4:
                category_data = {
                    source_id: document.getElementById('source-geological-dangers').value,
                    magnitude: document.getElementById('magnitude').value,
                    epicenter: document.getElementById('epicenter').value,
                    geography: document.getElementById('geography-geological-dangers').value,
                    description: document.getElementById('description-geological-dangers').value,
                }
                break;
            case 5:
                category_data = {
                    source_id: document.getElementById('source-hydrological-dangers').value,
                    height: document.getElementById('height').value,
                    water_name: document.getElementById('water_name').value,
                    description: document.getElementById('description-hydrological-dangers').value,
                }
                break;
            case 6:
                category_data = {
                    source_id: document.getElementById('source-emergency-situations').value,
                    geography: document.getElementById('geography-emergency-situations').value,
                    description: document.getElementById('description-emergency-situations').value,
                }
                break;
            case 7:
                category_data = {
                    source_id: document.getElementById('source-other-dangers').value,
                    description: document.getElementById('description-other-dangers').value
                }
                break;
            default:
                console.error("Unknown category_id:", base_data.category_id);
        }

        for (const [fieldId, value] of Object.entries(category_data)) {
            const error = validateField(fieldId, value);
            if (error) {
                errors[fieldId] = error;
                isValid = false;
                markFieldAsInvalid(fieldId, error);
            } else {
                markFieldAsValid(fieldId);
            }
        }

        if (!isValid) {
            return;
        }

        let event_url, method;
        const category = categories.find(cat => cat.key === parseInt(base_data.category_id));

        if (eventID) {
            event_url = `${window.APP_CONFIG.API_BASE_URL}/api/events/${eventID}/update/`;
            category_url = `${window.APP_CONFIG.API_BASE_URL}/api/${category.label}/by-event/${eventID}/`;
            method = 'PUT';
        } else {
            event_url = `${window.APP_CONFIG.API_BASE_URL}/api/events/`;
            category_url = `${window.APP_CONFIG.API_BASE_URL}/api/${category.label}/`
            method = 'POST';
        }
        
        const response = await fetch(event_url, {
            method: method,
            headers: {
                'Content-Type': 'application/json', 
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(base_data),
        });
        
        if (!response.ok) {
            const error = new Error(`HTTP error! status: ${response.status}`);
            error.status = response.status;
            throw error;
        }

        const data = await response.json();
        
        category_data.event_id=data.id
        
        const category_response = await fetch(category_url, {
            method: method,
            headers: {
                'Content-Type': 'application/json', 
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(category_data),
        });

        if (!category_response.ok) {
            const error = new Error(`HTTP error! status: ${category_response.status}`);
            error.status = category_response.status;
            throw error;
        }
        if (!eventID) {
            // Отправляем локальные меры
            for (const measure of window.localMeasures || []) {
                await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/measures/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        ...measure,
                        event_id: data.id
                    })
                });
            }
            // Очищаем локальные меры
            window.localMeasures = [];
        }
        window.updateAttachmentsEventId(data.id);
        window.location.href = `/information?event_id=${data.id}`;
        return data;

    } catch (error) {
        handleError(error, error.status);
    }

}
    async function handleSave() {
        saveButton.disabled = true;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Сохранение...';
            
        try {
            const eventId = getEventIdFromUrl();
                if (eventId) {
                    await sendData(eventId);
                } else {
                    await sendData(null)
            }
        } catch (error) {
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = 'Сохранить';
        }
    }
    saveButton.addEventListener('click', handleSave);
});
