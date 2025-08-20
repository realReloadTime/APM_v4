document.addEventListener('DOMContentLoaded', function () {
    const accessToken = localStorage.getItem('access_token');
    let allSubsystems = [];

    function handleError(error, status) {
        console.error('Ошибка:', error);
        alert(`Произошла ошибка: ${error.message || status || 'Неизвестная ошибка'}`);
    }

    async function loadData(object) {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/${object}/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            if (object === 'subsystems') {
                allSubsystems = data;
            }

            renderObject(object, data);

        } catch (error) {
            handleError(error, error.status);
        }
    }

    function renderObject(object, data) {
        const objectSelect = document.getElementsByName(object);
        if (!objectSelect || objectSelect.length === 0) {
            console.error('Element not found:', object);
            return;
        }

        objectSelect.forEach(select => {
            select.innerHTML = '';
        });

        if (data.length === 0) {
            const option = document.createElement('option');
            option.textContent = '--------';
            objectSelect.forEach(select => {
                select.appendChild(option.cloneNode(true));
            });
            return;
        }

        const sortedData = [...data].sort((a, b) => a.id - b.id);
        sortedData.forEach(data_object => {
            objectSelect.forEach(select => {
                const option = document.createElement('option');
                option.value = data_object['id'];
                option.textContent = data_object['name'];
                select.appendChild(option);
            });
        });
    }

    async function loadObjectTypes() {
        try {
            const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/object_types/`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const objectTypes = await response.json();

            for (const type of objectTypes) {
                try {
                    const objects = await loadObjectsByType(type.id);
                    renderObjectsInModal(type, objects);
                } catch (error) {
                    console.error(`Error loading objects for type ${type.id}:`, error);
                }
            }

        } catch (error) {
            handleError(error);
        }
    }

    async function loadObjectsByType(typeId) {
        const selectedLoaId = document.getElementById('loas').value;
        let url = `${window.APP_CONFIG.API_BASE_URL}/api/objects/?object_type_id=${typeId}`;

        if (selectedLoaId) {
            url += `&loa=${selectedLoaId}`;
        }
        try {
            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();

        } catch (error) {
            handleError(error);
            return [];
        }
    }

    function renderObjectsInModal(type, objects) {
        const oneObjectTab = document.querySelector('#oneObjectTab');
        const oneObjectTabContent = document.querySelector('#oneObjectTabContent');

        const multObjectTab = document.querySelector('#multObjectTab');
        const multObjectTabContent = document.querySelector('#multObjectTabContent');

        createObjectTab(type, objects, oneObjectTab, oneObjectTabContent, false);
        createObjectTab(type, objects, multObjectTab, multObjectTabContent, true);
    }

   function createObjectTab(type, objects, tabContainer, contentContainer, isMultiple) {
        const tabId = `tab-${type.id}-${isMultiple ? 'multi' : 'single'}`;
        let tabPane = document.getElementById(tabId);
        
        if (!tabPane) {
            const tabButton = document.createElement('li');
            tabButton.className = 'nav-item';
            tabButton.innerHTML = `
                <button class="nav-link" id="${tabId}-tab" data-bs-toggle="tab" 
                    data-bs-target="#${tabId}" type="button" role="tab">${type.name}</button>
            `;
            
            tabContainer.insertBefore(tabButton, tabContainer.lastElementChild);
            
            tabPane = document.createElement('div');
            tabPane.className = 'tab-pane fade';
            tabPane.id = tabId;
            tabPane.role = 'tabpanel';
            tabPane.setAttribute('aria-labelledby', `${tabId}-tab`);
            contentContainer.appendChild(tabPane);
        }
        
        const tableHtml = createObjectsTable(objects, isMultiple);
        tabPane.innerHTML = tableHtml;
        
        addObjectSelectionHandlers(tabPane, isMultiple);
    }

    function createObjectsTable(objects, isMultiple) {
        if (objects.length === 0) {
            return '<div class="p-3 text-center">Объекты не найдены</div>';
        }

        let tableHtml = `
            <div class="table-responsive">
                <table class="table table-primary table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Объект</th>
                            <th scope="col">Участвует в событии</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        objects.forEach(obj => {
            tableHtml += `
                <tr>
                    <td>${obj.name}</td>
                    <td>
                        <input type="${isMultiple ? 'checkbox' : 'radio'}" 
                               class="form-check" 
                               name="${isMultiple ? 'multObject' : 'oneObject'}" 
                               value="${obj.id}"
                               data-name="${obj.name}">
                    </td>
                </tr>
            `;
        });

        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;

        return tableHtml;
    }

    function addObjectSelectionHandlers(tabPane, isMultiple) {
        const selector = isMultiple ? 'input[type="checkbox"]' : 'input[type="radio"]';
        const inputs = tabPane.querySelectorAll(selector);

        inputs.forEach(input => {
            input.addEventListener('change', function () {
                if (!isMultiple) {
                    tabPane.querySelectorAll('input[type="radio"]').forEach(radio => {
                        if (radio !== input) radio.checked = false;
                    });
                }
            });
        });
    };

    function filterSubsystems() {
        const systemId = document.getElementById('systems').value;
        const subsystemSelect = document.getElementById('subsystems');

        subsystemSelect.innerHTML = '<option value="">Выберите подсистему</option>';

        if (!systemId) return;

        const filteredSubsystems = allSubsystems.filter(
            subsystem => subsystem.system_id == systemId
        );
        filteredSubsystems.forEach(subsystem => {
            const option = document.createElement('option');
            option.value = subsystem.id;
            option.textContent = subsystem.name;
            subsystemSelect.appendChild(option);
        });
    }
    async function loadLocations() {
        const selectedLoaId = document.getElementById('loas').value;
        let url = `${window.APP_CONFIG.API_BASE_URL}/api/locations/`;

        if (selectedLoaId) {
            url += `by-loa/${selectedLoaId}`;
        }

        try {
            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            if (!response.ok) throw new Error('Failed to load locations');
            const locations = await response.json();
            renderObject("locations", locations);

        } catch (error) {
            console.error('Error loading locations:', error);
        }
    }

    document.getElementById('save-oneObject')?.addEventListener('click', function () {
        const selected = document.querySelector('#oneObjectModal input[name="oneObject"]:checked');
        if (selected) {
            document.getElementById('object_id').value = selected.value;
            document.getElementById('object').value = selected.getAttribute('data-name');
        }
        bootstrap.Modal.getInstance(document.getElementById('oneObjectModal')).hide();
    });

    document.getElementById('save-multObject')?.addEventListener('click', function () {
        const selected = document.querySelectorAll('#multObjectModal input[name="multObject"]:checked');
        const ids = [];
        const names = [];

        selected.forEach(input => {
            ids.push(input.value);
            names.push(input.getAttribute('data-name'));
        });

        document.getElementById('influenced_objects_id').value = ids.join(',');
        document.getElementById('influenced_objects').value = names.join(', ');
        bootstrap.Modal.getInstance(document.getElementById('multObjectModal')).hide();
    });

    document.getElementById('systems')?.addEventListener('change', filterSubsystems);
    document.getElementById('loas').addEventListener('change', function () {loadLocations(); loadObjectTypes();});

    loadData("categories");
    loadData("systems");
    loadData("subsystem_statuses");
    loadData("conditions");
    loadData("precipitations");
    loadData("sources");
    loadData("systems");
    loadData("loas").then(() => {
        loadLocations();
        loadObjectTypes();
    });
    loadData("subsystems").then(() => {
        filterSubsystems();
    });
});