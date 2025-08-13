let selectedFiles = [];
let currentFileIndex = null;

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileListContainer = document.getElementById('fileListContainer');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const accessToken = localStorage.getItem('access_token');
    
    function getEventIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('event_id');
    }
    
    let eventId = getEventIdFromUrl();
    console.log(eventId)

    function handleError(error, status) {
        console.error('Ошибка:', error);
        alert(`Произошла ошибка: ${error.message || status || 'Неизвестная ошибка'}`);
    }

    async function loadEventAttachments() {
        try {
            const response = await fetch(
                `${window.APP_CONFIG.API_BASE_URL}/api/events/${eventId}/`,
                { headers: { 'Authorization': `Bearer ${accessToken}` } }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const eventData = await response.json();
            const attachmentsIds = eventData.event_attachments_id || [];
            
            for (const attachmentId of attachmentsIds) {
                const attachmentResponse = await fetch(
                    `${window.APP_CONFIG.API_BASE_URL}/api/attachments/${attachmentId}/`,
                    { headers: { 'Authorization': `Bearer ${accessToken}` } }
                );
                
                if (!attachmentResponse.ok) continue;
                
                const attachment = await attachmentResponse.json();
                selectedFiles.push({
                    id: attachment.id,
                    name: attachment.name,
                    size: attachment.size,
                    serverFile: true,
                    hasEventId: true // Файл уже привязан к событию
                });
            }
            
            renderFileList();
        } catch (error) {
            handleError(error);
        }
    }

    if (eventId) {
        loadEventAttachments();
    }

    fileInput.addEventListener('change', function(e) {
        const newFiles = Array.from(e.target.files);
        
        newFiles.forEach(newFile => {
            const isDuplicate = selectedFiles.some(
                file => file.name === newFile.name && file.size === newFile.size
            );
            
            if (!isDuplicate) {
                // Добавляем файл с пометкой о привязке к событию
                const fileRecord = {
                    fileObject: newFile,
                    name: newFile.name,
                    size: newFile.size,
                    hasEventId: eventId !== null // Если eventId есть - файл сразу привязан
                };
                
                selectedFiles.push(fileRecord);
                uploadFile(newFile, fileRecord); // Передаем конкретную запись файла
            }
        });
        
        renderFileList();
        fileInput.value = '';
    });
    
    confirmDeleteBtn.addEventListener('click', function() {
        if (currentFileIndex !== null) {
            const file = selectedFiles[currentFileIndex];
            deleteFile(file);
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            modal.hide();
        }
    });
    
    function renderFileList() {
        fileListContainer.innerHTML = '';
        
        if (selectedFiles.length === 0) {
            fileListContainer.innerHTML = '<p class="text-muted">Файлы не выбраны</p>';
            return;
        }
        
        const list = document.createElement('ul');
        list.className = 'list-group';
        
        selectedFiles.forEach((file, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            const fileInfo = document.createElement('div');
            
            // Добавляем иконку статуса привязки
            let statusIcon = '';
            if (file.id) {
                statusIcon = file.hasEventId 
                    ? '<span class="text-success ms-2" title="Привязан к событию">✓</span>'
                    : '<span class="text-warning ms-2" title="Ожидает привязки">!</span>';
            }
            
            fileInfo.innerHTML = `
                <div class="d-flex align-items-center">
                    <strong>${file.name}</strong>
                    ${statusIcon}
                </div>
                <div class="text-muted small">${formatFileSize(file.size)}</div>
            `;
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn btn-danger btn-sm';
            removeBtn.innerHTML = '&times;';
            removeBtn.onclick = () => confirmDelete(file.name, index);
            
            listItem.appendChild(fileInfo);
            listItem.appendChild(removeBtn);
            list.appendChild(listItem);
        });
        
        fileListContainer.appendChild(list);
    }
    
    function confirmDelete(fileName, index) {
        currentFileIndex = index;
        document.getElementById('fileNameToDelete').textContent = fileName;
        const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        modal.show();
    }
    
    function uploadFile(file, fileRecord) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Если eventId известен, сразу привязываем файл
        if (eventId) {
            formData.append('event_id', eventId);
        }
        
        fetch(`${window.APP_CONFIG.API_BASE_URL}/api/attachments/`, {
            method: 'POST',
            body: formData,
            headers: { 'Authorization': `Bearer ${accessToken}` }
        })
        .then(response => {
            if (!response.ok) throw new Error('Upload failed');
            return response.json();
        })
        .then(data => {
            // Обновляем запись о файле
            fileRecord.id = data.id;
            fileRecord.serverFile = true;
            
            // Если файл был привязан к событию сразу
            if (eventId) {
                fileRecord.hasEventId = true;
            }
            
            console.log('Файл успешно загружен:', data);
            renderFileList(); // Обновляем список для отображения статуса
            
            // Если это временный файл (без eventId), добавляем в очередь для обновления
            if (!eventId) {
                fileRecord.hasEventId = false;
                console.log('Временный файл, ожидает привязки к событию');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            
            // Удаляем файл из списка при ошибке
            const index = selectedFiles.findIndex(f => f.name === file.name);
            if (index !== -1) {
                selectedFiles.splice(index, 1);
                renderFileList();
            }
            
            alert(`Ошибка загрузки файла ${file.name}: ${error.message}`);
        });
    }
    
    function deleteFile(file) {
        if (file.id) {
            fetch(`${window.APP_CONFIG.API_BASE_URL}/api/attachments/${file.id}/delete/`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${accessToken}` }
            })
            .then(response => {
                if (!response.ok) {
                    console.error('Delete failed:', response.status);
                }
            })
            .catch(error => console.error('Delete error:', error));
        }
        
        selectedFiles.splice(currentFileIndex, 1);
        renderFileList();
        currentFileIndex = null;
        
        const dataTransfer = new DataTransfer();
        selectedFiles
            .filter(f => f.fileObject)
            .forEach(f => dataTransfer.items.add(f.fileObject));
        fileInput.files = dataTransfer.files;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    window.updateAttachmentsEventId = function(newEventId) {
        eventId = newEventId;
        
        const temporaryFiles = selectedFiles.filter(file => file.id && !file.hasEventId);
        
        if (temporaryFiles.length === 0) return;
        
        console.log(`Обновление ${temporaryFiles.length} файлов с eventId=${newEventId}`);
        
        temporaryFiles.forEach(file => {
            fetch(`${window.APP_CONFIG.API_BASE_URL}/api/attachments/${file.id}/update/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ event_id: newEventId })
            })
            .then(response => {
                if (!response.ok) throw new Error('Update failed');
                file.hasEventId = true;
                console.log(`Файл ${file.name} привязан к событию`);
                renderFileList(); 
            })
            .catch(error => {
                console.error('Update error:', error);
                alert(`Ошибка привязки файла ${file.name} к событию`);
            });
        });
    };
});