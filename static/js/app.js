/**
 * Contract Explainer - Frontend JavaScript
 * Handles file upload, API communication, and UI updates
 */

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const progressText = document.getElementById('progressText');
const analysisContent = document.getElementById('analysisContent');
const bottomBannerAd = document.getElementById('bottomBannerAd');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const shareBtn = document.getElementById('shareBtn');
const retryBtn = document.getElementById('retryBtn');

// Current file being processed
let currentFile = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Contract Explainer loaded');
    
    // File upload handling
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    // Button handlers
    newAnalysisBtn.addEventListener('click', resetToUpload);
    shareBtn.addEventListener('click', shareResults);
    retryBtn.addEventListener('click', retryAnalysis);
});

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave() {
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        processFile(e.target.files[0]);
    }
}

function processFile(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    
    if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload PDF, Word document, or text file.');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File too large. Please upload files smaller than 16MB.');
        return;
    }
    
    currentFile = file;
    console.log('Processing file:', file.name, file.type, file.size);
    
    // Show processing state
    showProcessing();
    
    // Upload and analyze file
    uploadAndAnalyze(file);
}

async function uploadAndAnalyze(file) {
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Update progress
        updateProgress('Uploading file...');
        
        // Send to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show results
            showResults(result);
        } else {
            // Show error
            showError(result.error || 'Analysis failed. Please try again.');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError('Network error. Please check your connection and try again.');
    }
}

// UI State functions
function showProcessing() {
    hideAllSections();
    processingSection.classList.remove('hidden');
    
    // Simulate processing steps
    const steps = [
        'Extracting text from document...',
        'Understanding contract structure...',
        'Analyzing key sections...',
        'Identifying potential red flags...',
        'Generating plain English explanation...'
    ];
    
    let stepIndex = 0;
    const stepInterval = setInterval(() => {
        if (stepIndex < steps.length) {
            updateProgress(steps[stepIndex]);
            stepIndex++;
        } else {
            clearInterval(stepInterval);
        }
    }, 2000);
}

function showResults(result) {
    hideAllSections();
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');
    bottomBannerAd.classList.remove('hidden');
    
    // Update file info
    document.getElementById('fileName').textContent = result.filename;
    document.getElementById('wordCount').textContent = result.word_count || 0;
    
    // Process and display analysis
    const formattedAnalysis = formatAnalysis(result.analysis);
    analysisContent.innerHTML = formattedAnalysis;
    
    console.log('Results displayed successfully');
}

function showError(message) {
    hideAllSections();
    errorSection.classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
}

function hideAllSections() {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    bottomBannerAd.classList.add('hidden');
}

function updateProgress(message) {
    progressText.textContent = message;
}

// Analysis formatting function
function formatAnalysis(analysisText) {
    // Convert the AI response to properly formatted HTML
    let html = analysisText;
    
    // Replace markdown-style headers with proper HTML
    html = html.replace(/## Contract Type & Purpose/g, '<div class="analysis-section"><h2>📄 Contract Type & Purpose</h2>');
    html = html.replace(/## Key Sections/g, '</div><div class="analysis-section"><h2>🔍 Key Sections</h2>');
    html = html.replace(/## ⚠️ RED FLAGS/g, '</div><div class="analysis-section red-flags"><h2>⚠️ RED FLAGS</h2>');
    html = html.replace(/## BOTTOM LINE/g, '</div><div class="analysis-section bottom-line"><h2>✅ BOTTOM LINE</h2>');
    
    // Close the last section
    html += '</div>';
    
    // Convert line breaks to paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraphs if not already wrapped
    if (!html.startsWith('<div')) {
        html = '<p>' + html + '</p>';
    }
    
    // Bold important terms
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return html;
}

// Action functions
function resetToUpload() {
    hideAllSections();
    uploadSection.classList.remove('hidden');
    fileInput.value = '';
    currentFile = null;
    console.log('Reset to upload state');
}

function retryAnalysis() {
    if (currentFile) {
        processFile(currentFile);
    } else {
        resetToUpload();
    }
}

function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'Contract Explainer - AI Analysis Results',
            text: 'I just got my contract explained in plain English using AI! Check out this free tool:',
            url: window.location.href
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback - copy URL to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            // Show temporary success message
            const originalText = shareBtn.textContent;
            shareBtn.textContent = 'Link Copied!';
            shareBtn.classList.add('bg-green-600');
            shareBtn.classList.remove('bg-blue-600');
            
            setTimeout(() => {
                shareBtn.textContent = originalText;
                shareBtn.classList.remove('bg-green-600');
                shareBtn.classList.add('bg-blue-600');
            }, 2000);
        }).catch(() => {
            alert('Unable to copy link. Please copy the URL manually.');
        });
    }
}

// Analytics tracking (optional)
function trackEvent(eventName, eventData = {}) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventData);
    }
    console.log('Event tracked:', eventName, eventData);
}

// Track file uploads
document.addEventListener('fileProcessed', (e) => {
    trackEvent('file_analyzed', {
        file_type: e.detail.type,
        file_size: e.detail.size
    });
});