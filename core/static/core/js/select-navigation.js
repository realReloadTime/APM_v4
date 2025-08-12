function setupSelectNavigation(selectId) {
    const select = document.getElementById(selectId);
    if (!select) return; 
    
    const prevBtn = select.previousElementSibling;
    const nextBtn = select.nextElementSibling;
    
    prevBtn?.addEventListener('click', () => {
        select.selectedIndex = (select.selectedIndex - 1 + select.options.length) % select.options.length;
        select.dispatchEvent(new Event('change'));
    });
    
    nextBtn?.addEventListener('click', () => {
        select.selectedIndex = (select.selectedIndex + 1) % select.options.length;
        select.dispatchEvent(new Event('change'));
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('save-oneObject');
    const modal = document.getElementById('oneObjectModal');
    
    saveButton.addEventListener('click', function() {
        const activeTab = document.querySelector('.tab-pane.active');
        const selectedRadio = activeTab.querySelector('input[name="oneObjectRadios"]:checked');
        
        if (selectedRadio) {
            const row = selectedRadio.closest('tr');
            const objectName = row.querySelector('td:first-child').textContent;
            document.querySelector('input[name="picked_object"]').value = objectName;
            
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
            
            document.querySelector('[data-bs-target="#oneObjectModal"]').focus();
        } else {
            alert('Пожалуйста, выберите объект');
        }
    });
    
    const modalInstance = new bootstrap.Modal(modal, {
        focus: true, 
        keyboard: true
    });
    
    modal.addEventListener('show.bs.modal', function() {
        modal.removeAttribute('inert');
    });
    
    modal.addEventListener('hidden.bs.modal', function() {
        modal.setAttribute('inert', '');
    });
});

document.addEventListener('DOMContentLoaded', () => {
    setupSelectNavigation('conditions');
    setupSelectNavigation('precipitations');
});