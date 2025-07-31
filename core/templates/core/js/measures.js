document.addEventListener('DOMContentLoaded', function() {
    const modal = new bootstrap.Modal(document.getElementById('measuresModal'));
    const saveButton = document.getElementById('save-measure');
    const actionsTextarea = document.getElementById('actions');
    
    saveButton.addEventListener('click', function() {
        const date = document.getElementById('measure-date').value;
        const text = document.getElementById('measure-text').value;
        
        if (!text.trim()) {
            alert('Пожалуйста, введите описание меры');
            return;
        }
        
        addMeasureToTextarea(date, text);
        clearModalFields();
        modal.hide();
    });
    
    cancelButton.addEventListener('click', function() {
        clearModalFields();
        modal.hide();
    });
    
    document.getElementById('measuresModal').addEventListener('show.bs.modal', function() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('measure-date').value = today || '';
        document.getElementById('measure-text').value = '';
        document.getElementById('measure-text').focus();
    });
    
    function addMeasureToTextarea(date, text) {
        const formattedDate = formatDate(date);
        
        const newMeasure = `[${formattedDate}] ${text}`;
        
        if (actionsTextarea.value) {
            actionsTextarea.value = newMeasure + '\n' + actionsTextarea.value;
        } else {
            actionsTextarea.value = newMeasure;
        }
    }
    
    function formatDate(dateString) {
        const [year, month, day] = dateString.split('-');
        return `${day}.${month}.${year}`;
    }
    
    function clearModalFields() {
        document.getElementById('measure-text').value = '';
    }
});