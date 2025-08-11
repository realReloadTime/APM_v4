document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('access_token');

    function handleError(error, status) {
        console.error('Ошибка:', error);
        alert(`Произошла ошибка: ${error.message || status || 'Неизвестная ошибка'}`);
    }

    async function loadData(object, object_value, object_text){
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/${object}/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            renderObject(object, data, object_value, object_text);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    function renderObject(object, data, object_value, object_text) {
    const objectSelect = document.getElementsByName(object);
    if (!objectSelect) {
        console.error('Element not found:', object);
        return;
    }
    objectSelect.forEach(select => {
            select.innerHTML = '';
        })
    if (data.length === 0) {
        const option = document.createElement('option');
        option.textContent = '--------';
        objectSelect.forEach(select => {
            select.appendChild(option);
        })
        return;
    }

    data.forEach(data_object => {
        objectSelect.forEach(select => {
            const option = document.createElement('option');
            option.value = data_object[object_value || 'id'];
            option.textContent = data_object[object_text || 'name'];
            select.appendChild(option);
        }
        )
    });
}
    // async function loadObjectTypes(isOneObject) {
    //     try {
    //         const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/object_types/`, {
    //             headers: { 'Authorization': `Bearer ${accessToken}` }
    //         });

    //         if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    //         const data = await response.json();
    //         renderObjectTypes(data, isOneObject);
    //     } catch (error) {
    //         handleError(error, error.status);
    //     }
    // }
    // async function loadObjects(objectType) {
    //     try {
    //         const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/object/object_types/`, {
    //             headers: { 'Authorization': `Bearer ${accessToken}` }
    //         });

    //         if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    //         const data = await response.json();
    //         renderObjectTypes(data, isOneObject);
    //     } catch (error) {
    //         handleError(error, error.status);
    //     }
    // }
    // function renderObjectTypes(data, isOneObject){
    //     if (isOneObject){
    //         const modal = document.getElementById('oneObjectModal');
    //     } else {
    //         const modal = document.getElementById("multObjectModal");
    //     }
    //     modal.innerHTML = "";
    //     data.forEach(data_object => {

    //         data_object.forEach(object => {
    //             const option = document.createElement('option');
    //             option.value = data_object[object_value || 'id'];
    //             option.textContent = data_object[object_text || 'name'];
    //             select.appendChild(option);
    //         }
    //         )
    //     });
    // } 
    loadData("loas", "id", "name");
    loadData("locations", "id", "name");
    loadData("categories", "id", "name");
    loadData("systems", "id", "name");
    loadData("subsystems", "id", "name");
    loadData("subsystem_statuses", "id", "name");
    loadData("conditions", "id", "name");
    loadData("precipitations", "id", "name");
    loadData("sources", "id", "name");
    // loadObjectTypes(isOneObject=true);
});