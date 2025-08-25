document.addEventListener('DOMContentLoaded', function () {
  const accessToken = localStorage.getItem('access_token');
  const eventsTableBody = document.getElementById('eventsTableBody');
  const paginationContainer = document.getElementById('paginationContainer');
  const recordsPerPageSelect = document.getElementById('recordsPerPage');
  const paginationInfo = document.querySelector('.pagination-info');

  let currentPage = 1;
  let totalPages = 1;
  let totalItems = 0;
  let currentPageSize = 10;
  const defaultPageSize = 10;
  let categoriesFilterSelect, loasFilterSelect, locationsFilterSelect;
  let currentFilters = {};
  let sortFields = {}; // Объект для хранения состояния сортировки {field: direction}
  let pickAll = true;

  let isFirstWebSocketConnection = true;

  if (!accessToken) {
    window.loadUserProfile();
    return;
  }

  async function loadFilterData() {
    try {
      const categoriesResponse = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/categories/`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (!categoriesResponse.ok) throw new Error('Failed to load categories');
      const categories = await categoriesResponse.json();
      populateSelect(categoriesFilterSelect, categories, 'Выберите категорию');

      const loasResponse = await fetch(`${window.APP_CONFIG.API_BASE_URL}/api/loas/`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (!loasResponse.ok) throw new Error('Failed to load loas');
      const loas = await loasResponse.json();
      populateSelect(loasFilterSelect, loas, 'Выберите филиал');

      await loadLocations();

    } catch (error) {
      console.error('Error loading filter data:', error);
    }
  }

  function populateSelect(select, items, placeholder) {
    select.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = placeholder;
    select.appendChild(defaultOption);

    items.forEach(item => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.name;
      select.appendChild(option);
    });
  }

  async function loadLocations() {
    const selectedLoaId = loasFilterSelect.value;
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
      populateSelect(locationsFilterSelect, locations, 'Выберите место');

      if (currentFilters.location) {
        locationsFilterSelect.value = currentFilters.location;
      }
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  }

  function saveFilters() {
    currentFilters = {
      show: document.querySelector('input[name="showEvents"]:checked').id,
      begin: document.getElementById('begin').value,
      end: document.getElementById('end').value,
      category: categoriesFilterSelect.value,
      loa: loasFilterSelect.value,
      location: locationsFilterSelect.value
    };
    localStorage.setItem('eventFilters', JSON.stringify(currentFilters));
  }

  function restoreFilters() {
    const savedFilters = localStorage.getItem('eventFilters');
    if (savedFilters) {
      currentFilters = JSON.parse(savedFilters);

      if (currentFilters.show) document.getElementById(currentFilters.show).checked = true;
      if (currentFilters.begin) document.getElementById('begin').value = currentFilters.begin;
      if (currentFilters.end) document.getElementById('end').value = currentFilters.end;
      if (currentFilters.category) categoriesFilterSelect.value = currentFilters.category;
      if (currentFilters.loa) loasFilterSelect.value = currentFilters.loa;
      if (currentFilters.location) locationsFilterSelect.value = currentFilters.location;
    }
  }

  function applyFiltersToURL(urlObj) {
    if (currentFilters.show && currentFilters.show !== 'showAll') {
      if (currentFilters.show == "showEnded") {
        urlObj.searchParams.set('is_ended', true);
      }
      else {
        urlObj.searchParams.set('is_ended', false);
      }
    }

    if (currentFilters.begin) urlObj.searchParams.set('start_date', currentFilters.begin);
    if (currentFilters.end) urlObj.searchParams.set('end_date', currentFilters.end);
    if (currentFilters.category) urlObj.searchParams.set('category', currentFilters.category);
    if (currentFilters.loa) urlObj.searchParams.set('loa', currentFilters.loa);
    if (currentFilters.location) urlObj.searchParams.set('location', currentFilters.location);

    const sortParams = getSortParams();
    if (sortParams) {
      urlObj.searchParams.set('sort_by', sortParams);
    }
  }

  function getSortParams() {
    const sortFieldsArray = [];

    for (const [field, direction] of Object.entries(sortFields)) {
      const prefix = direction === 'desc' ? '-' : '';
      sortFieldsArray.push(`${prefix}${field}`);
    }

    return sortFieldsArray.length > 0 ? sortFieldsArray.join(',') : null;
  }

  async function loadEvents(page = 1, pageSize = defaultPageSize) {
    try {
      const url = new URL(`${window.APP_CONFIG.API_BASE_URL}/api/events/`);
      applyFiltersToURL(url);

      url.searchParams.set('page', page);
      url.searchParams.set('page_size', pageSize);

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      renderEventsTable(data.results);
      updatePagination(data.total, data.page, data.page_size);
      updateRecordsInfo(data.total, data.page, data.page_size);

    } catch (error) {
      console.error('Ошибка загрузки событий:', error);
      eventsTableBody.innerHTML = `<tr><td colspan="9">Ошибка загрузки данных: ${error.message}</td></tr>`;
    }
  }

  function updateSortUI() {
    document.querySelectorAll('.sort-icon').forEach(icon => {
      icon.textContent = '';
    });

    for (const [field, direction] of Object.entries(sortFields)) {
      const header = document.querySelector(`th[data-sort="${field}"]`);
      if (header) {
        const icon = header.querySelector('.sort-icon');
        if (icon) {
          icon.textContent = direction === 'asc' ? '↑' : '↓';
        }
      }
    }
  }

  function handleHeaderClick() {
    const field = this.dataset.sort;

    if (!sortFields[field]) {
      sortFields[field] = 'desc';
    } else if (sortFields[field] === 'desc') {
      sortFields[field] = 'asc';
    } else {
      delete sortFields[field];
    }

    updateSortUI();
    loadEvents(currentPage, currentPageSize);
  }

  function renderEventsTable(events) {
    eventsTableBody.innerHTML = '';

    if (!events || events.length === 0) {
      eventsTableBody.innerHTML = `<tr><td colspan="9">Нет данных для отображения</td></tr>`;
      return;
    }

    events.forEach(event => {
      const row = document.createElement('tr');
      row.dataset.id = event.id;

      row.addEventListener('dblclick', function () {
        const eventId = this.dataset.id;
        window.location.href = `/information?event_id=${eventId}`;
      });

      row.innerHTML = `
        <td>${formatDateTime(event.begin)}</td>
        <td>${event.loa || '-'}</td>
        <td>${event.category || '-'}</td>
        <td>${event.location || '-'}</td>
        <td>${event.note || '-'}</td>
        <td>${event.end ? formatDateTime(event.end) : '-'}</td>
        <td>${(event.event_attachments_id && event.event_attachments_id.length > 0) ? 'Да' : 'Нет'}</td>
        <td><input name="table-check" id="${event.id}" type="checkbox" class="form-check" ${pickAll ? 'checked' : ''}></td>
        <td>
          <button class="btn btn-sm btn-primary edit-btn" data-id="${event.id}">
            <img src="${staticUrl}pencil.svg" 
                width="16" height="16" style="filter: invert(1);" alt="Редактировать">
          </button>
        </td>
      `;
      eventsTableBody.appendChild(row);
    });

    document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', function () {
        const eventId = this.getAttribute('data-id');
        window.location.href = `/form?event_id=${eventId}`;
      });
    });
  }

  function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
  }

  async function makeReport() {
    let reportIds = { "event_id": [] }
    document.getElementsByName("table-check").forEach(check => {
      if (check.checked) {
        reportIds.event_id.push(parseInt(check.id))
      }
    })
    const url = new URL(`${window.APP_CONFIG.API_BASE_URL}/api/report/`);

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${accessToken}` },
      body: JSON.stringify(reportIds)
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  }
  function changeCheck() {
    document.getElementsByName("table-check").forEach(check => {
      check.checked = pickAll;
    })
  }

  function updatePagination(totalItemsCount, currentPageArg, pageSizeFromServer) {
    totalItems = totalItemsCount;
    currentPage = currentPageArg;
    currentPageSize = pageSizeFromServer;
    totalPages = Math.ceil(totalItems / currentPageSize);

    paginationContainer.innerHTML = '';

    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = startPage + maxVisiblePages - 1;

    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    createPaginationButton('<<', 'first-page', currentPage === 1);
    createPaginationButton('<', 'prev-page', currentPage === 1);

    for (let i = startPage; i <= endPage; i++) {
      const pageLi = document.createElement('li');
      pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
      pageLi.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
      paginationContainer.appendChild(pageLi);
    }

    createPaginationButton('>', 'next-page', currentPage === totalPages);
    createPaginationButton('>>', 'last-page', currentPage === totalPages);
  }

  function updateRecordsInfo(totalItems, currentPage, pageSize) {
    const startItem = Math.min((currentPage - 1) * pageSize + 1, totalItems);
    const endItem = Math.min(currentPage * pageSize, totalItems);

    paginationInfo.innerHTML = `Показано ${startItem}-${endItem} из ${totalItems} записей`;
  }

  function createPaginationButton(symbol, className, isDisabled) {
    const li = document.createElement('li');
    li.className = `page-item ${isDisabled ? 'disabled' : ''}`;
    li.innerHTML = `<a class="page-link ${className}" href="#">${symbol}</a>`;
    paginationContainer.appendChild(li);
  }

  function setupEventListeners() {
    paginationContainer.addEventListener('click', (e) => {
      e.preventDefault();

      if (e.target.classList.contains('first-page') && currentPage > 1) {
        loadEvents(1, currentPageSize);
      }
      else if (e.target.classList.contains('prev-page') && currentPage > 1) {
        loadEvents(currentPage - 1, currentPageSize);
      }
      else if (e.target.classList.contains('next-page') && currentPage < totalPages) {
        loadEvents(currentPage + 1, currentPageSize);
      }
      else if (e.target.classList.contains('last-page') && currentPage < totalPages) {
        loadEvents(totalPages, currentPageSize);
      }
      else if (e.target.classList.contains('page-link')) {
        const page = parseInt(e.target.dataset.page);
        if (page && page !== currentPage) {
          loadEvents(page, currentPageSize);
        }
      }
    });

    recordsPerPageSelect.addEventListener('change', (e) => {
      let newPageSize = parseInt(e.target.value);

      if (isNaN(newPageSize) || newPageSize < 1) {
        newPageSize = defaultPageSize;
        recordsPerPageSelect.value = defaultPageSize;
      } else if (newPageSize > 1000) {
        newPageSize = 1000;
        recordsPerPageSelect.value = 1000;
      }

      currentPageSize = newPageSize;
      loadEvents(1, newPageSize);
    });
  }

  function initWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const accessToken = localStorage.getItem('access_token');
    const wsUrl = `${wsProtocol}//${wsHost}/ws/events/?token=${encodeURIComponent(accessToken)}`;

    const socket = new WebSocket(wsUrl);
    let reconnectAttempts = 0;

    socket.onopen = () => {
      console.log('WebSocket connected');

      if (!isFirstWebSocketConnection) {
        console.log('Refreshing data after reconnection');
        loadEvents(currentPage, currentPageSize);
      } else {
        isFirstWebSocketConnection = false;
      }
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'event.update') {
        console.log('Received event update:', message.data);
        loadEvents(currentPage, currentPageSize);
      } else if (message.type === 'auth_error') {
        console.error('WebSocket auth error, refreshing token...');
        refreshAccessToken()
          .then(newToken => {
            localStorage.setItem('access_token', newToken);
            initWebSocket();
          })
          .catch(error => {
            console.error('Token refresh failed:', error);
          });
      }
    };

    socket.onclose = (event) => {
      console.log('WebSocket closed:', event);

      const delay = Math.min(5000, 1000 * Math.pow(2, reconnectAttempts));
      reconnectAttempts++;
      setTimeout(initWebSocket, delay);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  function init() {
    const urlParams = new URLSearchParams(window.location.search);
    const initialPage = urlParams.get('page') || 1;
    const initialPageSize = urlParams.get('page_size') || defaultPageSize;

    recordsPerPageSelect.value = initialPageSize;
    currentPageSize = parseInt(initialPageSize);
    categoriesFilterSelect = document.getElementById('categoriesFilter');
    loasFilterSelect = document.getElementById('loasFilter');
    locationsFilterSelect = document.getElementById('locationsFilter');

    restoreFilters();
    loadFilterData();

    document.getElementById('makeReport').addEventListener('click', makeReport)
    pickAllButton = document.getElementById('pickAll')
    pickAllButton.addEventListener('click', function () {
      pickAll = !pickAll;
      if (pickAll) {
        pickAllButton.innerHTML = "Убрать выделение"
      }
      else {
        pickAllButton.innerHTML = "Выделить все"
      }
      changeCheck();
    });

    loasFilterSelect.addEventListener('change', loadLocations);

    document.getElementById('saveFilter').addEventListener('click', function () {
      saveFilters();
      loadEvents(1, currentPageSize);
    });

    setupEventListeners();
    loadEvents(parseInt(initialPage), parseInt(initialPageSize));

    document.querySelectorAll('th[data-sort]').forEach(header => {
      header.addEventListener('click', handleHeaderClick);
    });

    updateSortUI();

    initWebSocket();
  }

  init();
});