// Add class to prevent transitions during load
document.body.classList.add('preload');

document.addEventListener('DOMContentLoaded', function() {
    // Remove preload class after page has loaded
    setTimeout(function() {
        document.body.classList.remove('preload');
    }, 100);

    // Initialize collapsible functionality
    initializeCollapsible();
    
    // Initialize trigger row functionality
    initializeTriggerRows();
    
    // Initialize template selection
    initializeTemplateSelection();
});

// Collapsible section functionality
function initializeCollapsible() {
    const scheduleHeader = document.getElementById('schedule-header');
    const scheduleContent = document.getElementById('schedule-content');
    const scheduleToggleIcon = document.getElementById('schedule-toggle-icon');
    
    if (!scheduleHeader || !scheduleContent || !scheduleToggleIcon) return;
    
    // Check for stored preference - expand only if explicitly set to true
    const shouldBeExpanded = localStorage.getItem('scheduleExpanded') === 'true';
    
    // Apply stored preference (default is already collapsed via CSS)
    if (shouldBeExpanded) {
        scheduleContent.classList.add('expanded');
        scheduleToggleIcon.classList.add('expanded');
    }
    
    // Toggle functionality
    scheduleHeader.addEventListener('click', function() {
        const isCurrentlyExpanded = scheduleContent.classList.contains('expanded');
        
        if (isCurrentlyExpanded) {
            scheduleContent.classList.remove('expanded');
            scheduleToggleIcon.classList.remove('expanded');
            localStorage.setItem('scheduleExpanded', 'false');
        } else {
            scheduleContent.classList.add('expanded');
            scheduleToggleIcon.classList.add('expanded');
            localStorage.setItem('scheduleExpanded', 'true');
        }
    });
}

// Trigger row functionality
function initializeTriggerRows() {
    const addTriggerButton = document.getElementById('add-trigger-row');
    const triggerContainer = document.getElementById('trigger-container');
    
    if (!addTriggerButton || !triggerContainer) return;
    
    // Add new trigger row
    addTriggerButton.addEventListener('click', function() {
        // Get the first trigger row to clone its select options
        const firstRow = document.querySelector('.trigger-row');
        if (!firstRow) return;
        
        // Clone the select element with all its options
        const newSelect = firstRow.querySelector('.trigger-select').cloneNode(true);
        // Set proper array name
        newSelect.name = 'day[]';
        
        // Create new row
        const newRow = document.createElement('div');
        newRow.className = 'trigger-row';
        
        // Create time input
        const timeInput = document.createElement('input');
        timeInput.type = 'time';
        timeInput.name = 'time[]'; // Use array notation
        timeInput.className = 'trigger-time';
        
        // Create action div with remove button
        const actionDiv = document.createElement('div');
        actionDiv.className = 'trigger-action';
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-trigger-btn';
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', function() {
            newRow.remove();
        });
        
        // Assemble the elements
        actionDiv.appendChild(removeBtn);
        newRow.appendChild(newSelect);
        newRow.appendChild(timeInput);
        newRow.appendChild(actionDiv);
        
        // Add to container
        triggerContainer.appendChild(newRow);
    });
    
    // Set up existing remove buttons
    const removeButtons = document.querySelectorAll('.remove-trigger-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.trigger-row').remove();
        });
    });
}

// Template selection functionality
function initializeTemplateSelection() {
    const templateItems = document.querySelectorAll('.template-item');
    const selectedTemplatesInput = document.querySelector('input[name="selected_templates"]');
    
    if (!templateItems.length || !selectedTemplatesInput) return;
    
    const selectedTemplates = new Set();
    
    // Add click handlers
    templateItems.forEach(item => {
        item.addEventListener('click', function() {
            const templateId = this.dataset.templateId;
            
            if (selectedTemplates.has(templateId)) {
                // Deselect
                this.classList.remove('selected');
                selectedTemplates.delete(templateId);
            } else {
                // Select
                this.classList.add('selected');
                selectedTemplates.add(templateId);
            }
            
            // Update hidden input
            selectedTemplatesInput.value = Array.from(selectedTemplates).join(',');
        });
    });
}