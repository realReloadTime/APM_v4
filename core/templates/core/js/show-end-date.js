document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.getElementById('is_ended');
    const endDateBlock = document.getElementById('event-end');
        
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            endDateBlock.style.display = 'grid';
        } else {
            endDateBlock.style.display = 'none';
        }
    });
        
    if (checkbox.checked) {
        endDateBlock.style.display = 'grid';
    }
});