// Global variables
let currentDocumentText = '';
let currentDocumentName = '';
let currentDocumentId = '';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const chatSection = document.getElementById('chatSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.querySelector('.send-btn');
const summaryText = document.getElementById('summaryText');
const documentName = document.getElementById('documentName');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
    setupFileInput();
});

function setupDragAndDrop() {
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
}

function setupFileInput() {
    fileInput.addEventListener('change', handleFileSelect);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid file type (PDF, DOCX, or TXT)');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }

    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('document', file);

    showLoading('Processing your document...');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.error) {
            showError(data.error);
        } else {
            currentDocumentText = data.originalText;
            currentDocumentName = data.filename;
            currentDocumentId = data.documentId;
            displayResults(data.summary);
        }
    })
    .catch(error => {
        hideLoading();
        showError('An error occurred while processing your document. Please try again.');
        console.error('Upload error:', error);
    });
}

function displayResults(summary) {
    // Update document name
    documentName.textContent = currentDocumentName;
    
    // Display summary
    summaryText.textContent = summary;
    
    // Switch to chat section
    uploadSection.style.display = 'none';
    chatSection.style.display = 'block';
    
    // Clear chat messages except the initial bot message
    const initialMessage = chatMessages.querySelector('.bot-message');
    chatMessages.innerHTML = '';
    chatMessages.appendChild(initialMessage);
    
    // Focus on chat input
    chatInput.focus();
}

function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    chatInput.value = '';

    // Disable send button and show loading
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    // Send message to server
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: message,
            documentText: currentDocumentText,
            documentId: currentDocumentId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage('Sorry, I encountered an error while processing your question. Please try again.', 'bot');
        } else {
            addMessage(data.answer, 'bot');
        }
    })
    .catch(error => {
        addMessage('Sorry, I encountered an error while processing your question. Please try again.', 'bot');
        console.error('Chat error:', error);
    })
    .finally(() => {
        // Re-enable send button
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
    });
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const icon = document.createElement('i');
    icon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    
    messageContent.appendChild(icon);
    messageContent.appendChild(textP);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function resetApp() {
    // Reset file input
    fileInput.value = '';
    
    // Clear variables
    currentDocumentText = '';
    currentDocumentName = '';
    currentDocumentId = '';
    
    // Switch back to upload section
    chatSection.style.display = 'none';
    uploadSection.style.display = 'block';
    
    // Clear summary
    summaryText.textContent = '';
    
    // Reset chat messages
    chatMessages.innerHTML = `
        <div class="message bot-message">
            <div class="message-content">
                <i class="fas fa-robot"></i>
                <p>Hello! I've analyzed your document. Ask me anything about it!</p>
            </div>
        </div>
    `;
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const copyBtn = document.querySelector('.copy-btn');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        copyBtn.style.background = '#c6f6d5';
        copyBtn.style.color = '#2f855a';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '#f7fafc';
            copyBtn.style.color = '#4a5568';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

function showLoading(message) {
    loadingText.textContent = message;
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showError(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
    
    // Create and show new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    
    // Insert error message at the top of main content
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(errorDiv, mainContent.firstChild);
    
    // Auto-remove error message after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    // Remove existing success messages
    const existingSuccess = document.querySelectorAll('.success-message');
    existingSuccess.forEach(success => success.remove());
    
    // Create and show new success message
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    
    // Insert success message at the top of main content
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(successDiv, mainContent.firstChild);
    
    // Auto-remove success message after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 3000);
} 