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

document.addEventListener('DOMContentLoaded', () => {
    setupSelectNavigation('select-weather-condition');
    setupSelectNavigation('select-rainfall');
});