document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');
    const saveMeasureBtn = document.getElementById('save-measure');
    const measureDateEl = document.getElementById('measure-date');
    const measureTextEl = document.getElementById('measure-text');
    
    measureDateEl.value = formatToViewDateTime(new Date());
    
    function formatToViewDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return new Date(date.getTime() - (date.getTimezoneOffset() * 60000 ))
                    .toISOString().slice(0,16);
    }

    function formatToISODateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toISOString();
    }

    const measuresModalEl = document.getElementById('measuresModal');
    let measuresModal = null;
    
    if (measuresModalEl) {
        measuresModal = new bootstrap.Modal(measuresModalEl);
    }

    saveMeasureBtn.addEventListener('click', function() {
        const eventId = getEventIdFromUrl();
        const measure = {
            adopted_at: formatToISODateTime(measureDateEl.value),
            description: measureTextEl.value.trim()
        };
        
        if (!measure.description) {
            alert('Введите описание меры');
            return;
        }
        
        if (eventId) {
            saveMeasureToServer(measure, eventId);
        } else {
            if (!window.localMeasures) window.localMeasures = [];
            window.localMeasures.push(measure);
            updateLocalActionsTextarea();
        }
        
        
        measureTextEl.value = '';
        measureDateEl.value = formatToViewDateTime(new Date());
        
        if (measuresModal) {
            measuresModal.hide();
        }
    });
    
    function saveMeasureToServer(measure, eventId) {
        fetch(`${window.APP_CONFIG.API_BASE_URL}/api/measures/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                ...measure,
                event_id: eventId
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сохранения меры');
            return response.json();
        })
        .then(() => {
            if (typeof window.loadMeasures === 'function') {
                window.loadMeasures(eventId);
            }
        })
        .catch(error => {
            console.error('Ошибка сохранения меры:', error);
            alert('Не удалось сохранить меру');
        });
    }
    
    function getEventIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('event_id');
    }
    
    function updateLocalActionsTextarea() {
        const textarea = document.getElementById('actions');
        if (!textarea || !window.localMeasures) return;
        
        if (window.localMeasures.length === 0) {
            textarea.value = 'Принятые меры отсутствуют';
            return;
        }
        
        const sortedMeasures = [...window.localMeasures].sort(
            (a, b) => new Date(a.adopted_at) - new Date(b.adopted_at)
        );
        
        let text = '';
        sortedMeasures.forEach(measure => {
            const date = formatToViewDateTime(new Date(measure.adopted_at));
            text += `[${date}] ${measure.description}\n\n`;
        });
        
        textarea.value = text.trim();
    }
});