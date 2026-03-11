/**
 * Main JavaScript file for To-Do List Application
 * 
 * Contains utility functions and common functionality
 * used across the application
 */

/**
 * Utility function to format dates for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

/**
 * Utility function to escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show error message to user
 */
function showError(message) {
    console.error('Error:', message);
    // This can be extended to show toast notifications
}

/**
 * Show success message to user
 */
function showSuccess(message) {
    console.log('Success:', message);
    // This can be extended to show toast notifications
}
