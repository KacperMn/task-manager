/**
 * Share Desk page functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Copy button functionality
    const copyButton = document.getElementById('copy-button');
    const shareUrl = document.getElementById('share-url');
    
    if (copyButton && shareUrl) {
        copyButton.addEventListener('click', function() {
            shareUrl.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyButton.style.backgroundColor = 'var(--color-success, #28a745)';
            copyButton.style.color = '#fff';
            
            setTimeout(function() {
                copyButton.innerHTML = originalText;
                copyButton.style.backgroundColor = '';
                copyButton.style.color = '';
            }, 2000);
        });
    }
    
    // Auto-submit permission changes
    const permissionSelects = document.querySelectorAll('.permission-select');
    
    permissionSelects.forEach(select => {
        select.addEventListener('change', function() {
            const userId = this.getAttribute('data-user-id');
            const username = this.getAttribute('data-username');
            const form = document.getElementById(`permission-form-${userId}`);
            
            if (confirm(`Are you sure you want to change ${username}'s permission?`)) {
                form.submit();
            } else {
                // Reset to previous value if canceled
                const currentIndex = this.selectedIndex;
                this.selectedIndex = currentIndex === 0 ? 1 : 0;
            }
        });
    });
});