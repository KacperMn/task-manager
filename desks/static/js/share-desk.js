/**
 * Share Desk page functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Copy button functionality
    const copyButton = document.getElementById('copy-button');
    if (copyButton) {
        copyButton.addEventListener('click', copyShareLink);
    }
    
    // Permission select change handlers
    const permissionSelects = document.querySelectorAll('select[name="permission"]');
    permissionSelects.forEach(select => {
        select.addEventListener('change', function() {
            handlePermissionChange(this);
        });
    });
    
    // Remove user confirmation
    const removeButtons = document.querySelectorAll('.remove-user-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to remove this user?')) {
                e.preventDefault();
            }
        });
    });
});

/**
 * Copy share URL to clipboard
 */
function copyShareLink() {
    const shareUrl = document.getElementById("share-url");
    const copyButton = document.getElementById("copy-button");
    
    shareUrl.select();
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl.value)
            .then(() => {
                // Success feedback
                copyButton.innerHTML = '<i class="fas fa-check"></i> Copied';
                copyButton.classList.replace('btn-outline-primary', 'btn-success');
                
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    copyButton.classList.replace('btn-success', 'btn-outline-primary');
                }, 2000);
            })
            .catch(() => {
                document.execCommand('copy');
            });
    } else {
        document.execCommand('copy');
    }
}

/**
 * Handle permission change with confirmation
 */
function handlePermissionChange(selectElement) {
    const userId = selectElement.getAttribute('data-user-id');
    const username = selectElement.getAttribute('data-username');
    const permissionName = selectElement.options[selectElement.selectedIndex].text;
    
    if (confirm(`Change ${username}'s permission to "${permissionName}"?`)) {
        document.getElementById(`permission-form-${userId}`).submit();
    } else {
        // Reset selection if canceled
        selectElement.selectedIndex = [...selectElement.options].findIndex(
            option => option.hasAttribute('selected')
        );
    }
}