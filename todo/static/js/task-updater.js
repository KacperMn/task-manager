/**
 * Simple live task status updater
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const POLL_INTERVAL = 5000; // 5 seconds
    
    // Get desk slug from URL
    const pathParts = window.location.pathname.split('/').filter(p => p);
    const deskSlug = pathParts.length > 0 ? pathParts[0] : null;
    
    if (!deskSlug) {
        console.error('Could not determine desk slug from URL');
        return;
    }
    
    console.log('Task updater started for desk:', deskSlug);
    
    // Keep track of task states
    const taskStates = {};
    
    // Initial collection of task states
    function collectInitialTaskStates() {
        // Active tasks
        document.querySelectorAll('.task-list .task-item').forEach(item => {
            const form = item.querySelector('form');
            if (form) {
                const action = form.getAttribute('action');
                const taskId = extractTaskId(action);
                if (taskId) {
                    taskStates[taskId] = true;
                }
            }
        });
        
        // Inactive tasks
        document.querySelectorAll('.task-list-horizontal li').forEach(item => {
            const form = item.querySelector('form');
            if (form) {
                const action = form.getAttribute('action');
                const taskId = extractTaskId(action);
                if (taskId) {
                    taskStates[taskId] = false;
                }
            }
        });
        
        console.log('Tracking tasks:', Object.keys(taskStates).length);
    }
    
    // Extract task ID from action URL
    function extractTaskId(actionUrl) {
        if (!actionUrl) return null;
        
        // Match /toggle-task-status/<id>/
        const match = actionUrl.match(/toggle-task-status\/(\d+)/);
        return match ? match[1] : null;
    }
    
    // Check for task updates
    function checkForUpdates() {
        fetch(`/${deskSlug}/tasks/status/`)
            .then(response => response.json())
            .then(data => {
                console.log(`Received ${data.count} tasks at ${data.timestamp}`);
                
                // Process each task
                data.tasks.forEach(task => {
                    const taskId = task.id.toString();
                    
                    // Only care about tasks we're tracking
                    if (taskId in taskStates) {
                        // Check if state changed
                        if (taskStates[taskId] !== task.is_active) {
                            console.log(`Task ${taskId} state changed to ${task.is_active ? 'active' : 'inactive'}`);
                            
                            // Update our tracking
                            taskStates[taskId] = task.is_active;
                            
                            // Force page refresh for now
                            window.location.reload();
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error checking task status:', error);
            });
    }
    
    // Start the process
    collectInitialTaskStates();
    setInterval(checkForUpdates, POLL_INTERVAL);
    checkForUpdates(); // Check immediately
});