console.log('Toggle task script loaded!');

document.addEventListener('DOMContentLoaded', function() {
    // Set up task toggling with animation and proper text handling
    setupTaskToggling();
});

function setupTaskToggling() {
    const tasksContainer = document.querySelector('.tasks-container');
    
    // Single event listener for all task buttons (current and future)
    tasksContainer.addEventListener('click', function(event) {
        // Find the button that was clicked (if any)
        const button = event.target.closest('.list-btn');
        if (!button) return; // Not a button click
        
        // Get form and prepare request
        event.preventDefault();
        const form = button.closest('form');
        if (!form) return;
        
        // Set visual feedback immediately (optimistic UI)
        const listItem = button.closest('li');
        listItem.style.opacity = '0.5';
        button.disabled = true;
        
        // Extract clean task text
        const cleanTaskText = extractTaskText(button);
        
        // Send request
        toggleTaskStatus(form, cleanTaskText, listItem);
    });
}

function extractTaskText(button) {
    // Create temporary element to manipulate DOM
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = button.innerHTML;
    
    // Remove all icon spans
    const iconSpans = tempDiv.querySelectorAll('.list-btn-icon');
    iconSpans.forEach(span => span.remove());
    
    // Return clean text
    return tempDiv.textContent.trim();
}

function toggleTaskStatus(form, taskText, listItem) {
    const url = form.getAttribute('action');
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            moveTask(listItem, taskText, url, csrfToken, data.is_active);
            showNotification(data.message, 'success');
        } else {
            // Restore the item if there was an issue
            listItem.style.opacity = '1';
            listItem.querySelector('button').disabled = false;
            showNotification('Could not update task status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        listItem.style.opacity = '1';
        listItem.querySelector('button').disabled = false;
        showNotification('Error updating task status', 'error');
    });
}

function moveTask(listItem, taskText, url, csrfToken, isActive) {
    // Apply animation to existing item
    listItem.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    listItem.style.opacity = '0';
    listItem.style.transform = isActive ? 'translateX(-20px)' : 'translateX(20px)';
    
    // Create new item for destination list with animation preparation
    const newItem = document.createElement('li');
    if (isActive) {
        newItem.classList.add('task-item');
    }
    
    // Set HTML with clean task text
    newItem.innerHTML = `
        <form method="post" action="${url}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <button type="submit" class="list-btn ${isActive ? 'active' : 'inactive'}">
                ${taskText}
                <span class="list-btn-icon">${isActive ? '✓' : '+'}</span>
            </button>
        </form>
    `;
    
    // Prepare animation for the new item
    newItem.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    newItem.style.opacity = '0';
    newItem.style.transform = isActive ? 'translateX(20px)' : 'translateX(-20px)';
    
    // After a short delay, remove the old item and add the new one with animation
    setTimeout(() => {
        listItem.remove();
        
        if (isActive) {
            const activeList = document.querySelector('.task-list');
            activeList.appendChild(newItem);
        } else {
            const inactiveList = document.querySelector('.task-list-horizontal');
            inactiveList.appendChild(newItem);
        }
        
        // Trigger reflow to ensure animation works
        newItem.offsetHeight;
        
        // Show the new item with animation
        newItem.style.opacity = '1';
        newItem.style.transform = 'translateX(0)';
    }, 300);
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 20px;
        background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
        z-index: 1000;
    `;
    
    document.body.appendChild(notification);
    
    // Trigger animation to show
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Automatically remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(10px)';
        
        // Remove from DOM after animation completes
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}