document.addEventListener('DOMContentLoaded', function() {
    // Setup toggle functionality for both collapsible headers
    setupToggle('createScheduleToggle', 'createScheduleContent');
    setupToggle('viewSchedulesToggle', 'viewSchedulesContent');
    
    // Function to set up toggle behavior
    function setupToggle(toggleId, contentId) {
        const toggleBtn = document.getElementById(toggleId);
        const content = document.getElementById(contentId);
        
        if (toggleBtn && content) {
            toggleBtn.addEventListener('click', function() {
                // Toggle the expanded state
                const expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
                toggleBtn.setAttribute('aria-expanded', !expanded);
                
                // Toggle the content visibility
                if (content.style.display === 'none' || content.style.display === '') {
                    content.style.display = 'block';
                    toggleBtn.querySelector('.toggle-icon').style.transform = 'rotate(180deg)';
                } else {
                    content.style.display = 'none';
                    toggleBtn.querySelector('.toggle-icon').style.transform = 'rotate(0)';
                }
            });
        }
    }
    
    // Add moment button functionality for create form
    const addButton = document.getElementById('addMoment');
    if (addButton) {
        addButton.addEventListener('click', function() {
            const momentsContainer = document.querySelector('.moments-container');
            addNewMoment(momentsContainer, 'moments');
        });
    }
    
    // Add moment button functionality for edit forms
    document.querySelectorAll('.btn-add-moment[data-schedule-id]').forEach(button => {
        button.addEventListener('click', function() {
            const scheduleId = this.getAttribute('data-schedule-id');
            const momentsContainer = document.getElementById(`edit-moments-${scheduleId}`);
            const countInput = document.getElementById(`edit-moments-count-${scheduleId}`);
            
            if (momentsContainer && countInput) {
                const prefix = `edit-${scheduleId}`;
                const count = parseInt(countInput.value);
                addNewMoment(momentsContainer, prefix, count);
                countInput.value = count + 1;
            }
        });
    });
    
    // Generic function to add new moment to any container
    function addNewMoment(container, prefix, startIndex = 0) {
        const items = container.querySelectorAll('.moment-item');
        const newIndex = items.length;
        
        // Clone the first moment item
        const newItem = items[0].cloneNode(true);
        
        // Update the header text
        const headerSpan = newItem.querySelector('.moment-item-header span');
        headerSpan.textContent = `Moment #${newIndex + 1}`;
        
        // Add remove button if it doesn't exist
        let removeBtn = newItem.querySelector('.btn-remove');
        if (!removeBtn && newIndex > 0) {
            const header = newItem.querySelector('.moment-item-header');
            removeBtn = document.createElement('button');
            removeBtn.className = 'btn-remove';
            removeBtn.textContent = 'Remove';
            removeBtn.type = 'button';
            header.appendChild(removeBtn);
        }
        
        // Update form field names and IDs for the new index
        const inputs = newItem.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.name) {
                const newName = input.name.replace(/\d+/, newIndex);
                input.name = newName;
            }
            if (input.id) {
                const newId = input.id.replace(/\d+$/, newIndex + 1);
                input.id = newId;
            }
            
            // Reset values for new moment
            if (input.type !== 'hidden') {
                if (input.type === 'checkbox') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            }
        });
        
        // Add remove functionality
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                this.closest('.moment-item').remove();
            });
        }
        
        // Append the new item to the container
        container.appendChild(newItem);
    }
    
    // Add remove functionality to existing remove buttons
    document.querySelectorAll('.btn-remove').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.moment-item').remove();
        });
    });
    
    // Edit button functionality
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', function() {
            const scheduleId = this.getAttribute('data-schedule-id');
            const editForm = document.getElementById(`edit-form-${scheduleId}`);
            
            if (editForm) {
                // Toggle form visibility
                editForm.style.display = editForm.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
    
    // Cancel button functionality
    document.querySelectorAll('.btn-cancel').forEach(button => {
        button.addEventListener('click', function() {
            const scheduleId = this.getAttribute('data-schedule-id');
            const editForm = document.getElementById(`edit-form-${scheduleId}`);
            
            if (editForm) {
                // Hide the form
                editForm.style.display = 'none';
            }
        });
    });
});