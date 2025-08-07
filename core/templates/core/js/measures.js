document.addEventListener('DOMContentLoaded', function() {
    const modalEl = document.getElementById('measuresModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    const saveButton = document.getElementById('save-measure');
    const actionsTextarea = document.getElementById('actions');
    
    saveButton.addEventListener('click', function() {
        const date = document.getElementById('measure-date').value;
        const text = document.getElementById('measure-text').value;
        
        if (!text.trim()) {
            alert('Пожалуйста, введите описание меры');
            return;
        }
        if (!date.trim()) {
            alert('Пожалуйста, введите дату');
            return;
        }
        addMeasureToTextarea(date, text);
        clearModalFields();
        modal.hide();
        return false;
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
        if (!dateString) return 'дата не указана';
        const [year, month, day] = dateString.split('-');
        return `${day}.${month}.${year}`;
    }
    
    function clearModalFields() {
        document.getElementById('measure-text').value = '';
        document.getElementById('measure-date').value = '';
    }
});