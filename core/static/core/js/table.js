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

  let isFirstWebSocketConnection = true;

  if (!accessToken) {
    window.location.href = '/login';
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
      if (currentFilters.show == "showEnded"){
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
        <td>${event.attachments && event.attachments.length > 0 ? 'Да' : 'Нет'}</td>
        <td><input type="checkbox" class="form-check" ${event.report_required ? 'checked' : ''}></td>
        <td>
          <button class="btn btn-sm btn-primary edit-btn" data-id="${event.id}">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
              <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325"/>
            </svg> 
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
      const newPageSize = parseInt(e.target.value);
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

      // Обновляем данные только при переподключении
      if (!isFirstWebSocketConnection) {
        console.log('Refreshing data after reconnection');
        loadEvents(currentPage, currentPageSize);
      } else {
        // Помечаем первое подключение как завершенное
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
            // Обновляем токен и переподключаемся
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

      // Не сбрасываем флаг первого подключения здесь!
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
    
    loasFilterSelect.addEventListener('change', loadLocations);
    
    document.getElementById('saveFilter').addEventListener('click', function() {
        saveFilters();
        loadEvents(1, currentPageSize);
    });

    setupEventListeners();
    loadEvents(parseInt(initialPage), parseInt(initialPageSize));
    initWebSocket();
  }

  init();
});