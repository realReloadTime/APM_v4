document.addEventListener('DOMContentLoaded', function() {
    const save = document.getElementById('save');

    function getEventIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('event_id');
    }

    save.addEventListener('click', function() {
        const eventId = getEventIdFromUrl();
        if (eventId) {
            sendData(eventId);
        } else {
            
    }
    });
})