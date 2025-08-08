document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');
    const filialSelect = document.getElementById('filial');
    const categorySelect = document.getElementById('category');
    const locationSelect = document.getElementById('location');

    function handleError(error, status) {
        console.error('Ошибка:', error);
        alert(`Произошла ошибка: ${error.message || status || 'Неизвестная ошибка'}`);
    }

    async function loadFilial() {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/loas/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const filials = await response.json();
            renderFilial(filials);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    async function loadCategory() {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/categories/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const categories = await response.json();
            renderCategory(categories);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    async function loadLocation() {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/locations/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const locations = await response.json();
            renderLocation(locations);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    function renderFilial(filials) {
        filialSelect.innerHTML = '';
        
        if (filials.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'Нет доступных филиалов';
            filialSelect.appendChild(option);
            return;
        }

        filials.forEach(filial => {
            const option = document.createElement('option');
            option.value = filial.id;
            option.textContent = filial.name;
            filialSelect.appendChild(option);
        });
    }

    function renderLocation(locations) {
        locationSelect.innerHTML = '';
        

        if (locations.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'Нет доступных мест';
            locationSelect.appendChild(option);
            return;
        }

        locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location.id;
            option.textContent = location.name; 
            locationSelect.appendChild(option);
        });
    }
    
    function renderCategory(categories) {
        categorySelect.innerHTML = '';
        
        if (categories.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'Нет доступных категорий';
            categorySelect.appendChild(option);
            return;
        }

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.table_name;
            option.textContent = category.name;  
            categorySelect.appendChild(option);
        });
    }

    loadFilial();
    loadCategory();
    loadLocation();
});