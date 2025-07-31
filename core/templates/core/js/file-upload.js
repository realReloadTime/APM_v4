let selectedFiles = [];
let currentFileIndex = null;

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileListContainer = document.getElementById('fileListContainer');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    fileInput.addEventListener('change', function(e) {
        const newFiles = Array.from(e.target.files);
        
        newFiles.forEach(newFile => {
            const isDuplicate = selectedFiles.some(
                file => file.name === newFile.name && file.size === newFile.size
            );
            
            if (!isDuplicate) {
                selectedFiles.push(newFile);
            }
        });
        
        renderFileList();
        
        fileInput.value = '';
    });
    
    confirmDeleteBtn.addEventListener('click', function() {
        if (currentFileIndex !== null) {
            removeFile(currentFileIndex);
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
            fileInfo.innerHTML = `
                <strong>${file.name}</strong>
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
    
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        renderFileList();
        currentFileIndex = null;
        
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});