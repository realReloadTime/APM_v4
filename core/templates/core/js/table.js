document.addEventListener('DOMContentLoaded', function() {
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

  if (!accessToken) {
    window.location.href = '/login.html';
    return;
  }

  async function loadEvents(page = 1, pageSize = defaultPageSize, filters = {}) {
    try {
      const url = new URL(`${window.APP_CONFIG.API_BASE_URL}/api/events/`);
      url.searchParams.append('page', page);
      url.searchParams.append('page_size', pageSize);
      
      const urlParams = new URLSearchParams(window.location.search);
      for (const [key, value] of urlParams.entries()) {
        if (key !== 'page' && key !== 'page_size') {
          url.searchParams.append(key, value);
        }
      }

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
      eventsTableBody.innerHTML = `<tr><td colspan="8">Ошибка загрузки данных: ${error.message}</td></tr>`;
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
      row.dataset.id = event.id; // Сохраняем ID в атрибуте строки
      
      // Обработчик двойного клика
      row.addEventListener('dblclick', function() {
        const eventId = this.dataset.id;
        window.location.href = `information_page.html?event_id=${eventId}`;
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
          <button class="btn btn-sm btn-warning edit-btn" data-id="${event.id}">
            <i class="bi bi-pencil"></i> Редактировать
          </button>
        </td>
      `;
      eventsTableBody.appendChild(row);
    });

    // Добавляем обработчики для кнопок редактирования
    document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', function() {
        const eventId = this.getAttribute('data-id');
        window.location.href = `form_page.html?event_id=${eventId}`;
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

  function init() {
    const urlParams = new URLSearchParams(window.location.search);
    const initialPage = urlParams.get('page') || 1;
    const initialPageSize = urlParams.get('page_size') || defaultPageSize;
    
    recordsPerPageSelect.value = initialPageSize;
    currentPageSize = parseInt(initialPageSize);
    
    setupEventListeners();
    loadEvents(parseInt(initialPage), parseInt(initialPageSize));
  }

  init();
});