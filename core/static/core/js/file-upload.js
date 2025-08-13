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
    console.log("Initial eventId:", eventId);

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
            console.log("Found attachments:", attachmentsIds);
            
            for (const attachmentId of attachmentsIds) {
                const attachmentResponse = await fetch(
                    `${window.APP_CONFIG.API_BASE_URL}/api/attachments/${attachmentId}/`,
                    { headers: { 'Authorization': `Bearer ${accessToken}` } }
                );
                
                if (!attachmentResponse.ok) {
                    console.warn(`Attachment ${attachmentId} not found, status: ${attachmentResponse.status}`);
                    continue;
                }
                
                const attachment = await attachmentResponse.json();
                console.log("Loaded attachment:", attachment);
                
                selectedFiles.push({
                    id: attachment.id,
                    name: attachment.name,
                    size: attachment.size,
                    serverFile: true,
                    hasEventId: true
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
        console.log("New files selected:", newFiles.length);
        
        newFiles.forEach(newFile => {
            const isDuplicate = selectedFiles.some(
                file => file.name === newFile.name && file.size === newFile.size
            );
            
            if (!isDuplicate) {
                const fileRecord = {
                    fileObject: newFile,
                    name: newFile.name,
                    size: newFile.size,
                    hasEventId: eventId !== null
                };
                
                selectedFiles.push(fileRecord);
                console.log("Added file record:", fileRecord);
                uploadFile(newFile, fileRecord);
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
        
        // Всегда добавляем event_id, если он известен
        if (eventId) {
            formData.append('event_id', eventId);
            console.log("Uploading with event_id:", eventId);
        } else {
            console.log("Uploading without event_id");
        }
        
        fetch(`${window.APP_CONFIG.API_BASE_URL}/api/attachments/`, {
            method: 'POST',
            body: formData,
            headers: { 'Authorization': `Bearer ${accessToken}` }
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Upload failed: ${response.status} - ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Upload response:", data);
            
            fileRecord.id = data.id;
            fileRecord.serverFile = true;
            fileRecord.hasEventId = eventId !== null;
            
            if (eventId && data.event_id !== eventId) {
                console.warn("Server event_id mismatch:", data.event_id, "expected:", eventId);
                fileRecord.hasEventId = false;
            }
            
            renderFileList();
        })
        .catch(error => {
            console.error('Upload error:', error);
            
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
                    return response.text().then(text => {
                        console.error('Delete error text:', text);
                    });
                }
                console.log("File deleted:", file.id);
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
        console.log("Updating attachments with new eventId:", newEventId);
        eventId = newEventId;
        
        const temporaryFiles = selectedFiles.filter(file => file.id && !file.hasEventId);
        
        if (temporaryFiles.length === 0) {
            console.log("No temporary files to update");
            return;
        }
        
        console.log(`Updating ${temporaryFiles.length} files with eventId=${newEventId}`);
        
        temporaryFiles.forEach(file => {
            const url = `${window.APP_CONFIG.API_BASE_URL}/api/attachments/${file.id}/update/`;
            console.log(`Updating attachment: ${url}`);
            
            fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ event_id: newEventId })
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Update failed: ${response.status} - ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Update response:", data);
                file.hasEventId = true;
                renderFileList();
            })
            .catch(error => {
                console.error('Update error:', error);
                alert(`Ошибка привязки файла ${file.name} к событию: ${error.message}`);
            });
        });
    };
});