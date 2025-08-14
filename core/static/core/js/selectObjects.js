document.addEventListener('DOMContentLoaded', function () {
    const oneObjectModal = document.getElementById('oneObjectModal');
    if (oneObjectModal) {
        oneObjectModal.addEventListener('show.bs.modal', function () {
            const selectedId = document.getElementById('object_id').value;
            const radioInputs = oneObjectModal.querySelectorAll('input[type="radio"]');
            radioInputs.forEach(radio => {
                radio.checked = radio.value === selectedId;
            });
        });
    }
    const multObjectModal = document.getElementById('multObjectModal');
    if (multObjectModal) {
        multObjectModal.addEventListener('show.bs.modal', function () {
            const selectedIdsStr = document.getElementById('influenced_objects_id').value;
            const selectedIds = selectedIdsStr ? selectedIdsStr.split(',') : [];
            const checkboxInputs = multObjectModal.querySelectorAll('input[type="checkbox"]');
            checkboxInputs.forEach(checkbox => {
                checkbox.checked = selectedIds.includes(checkbox.value);
            });
        });
    }
});