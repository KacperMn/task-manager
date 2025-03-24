document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.toggle-task-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the form from submitting normally

            const taskId = form.getAttribute('data-task-id');
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

            // Send the POST request to toggle the task
            fetch(`/tasks/toggle-active/${taskId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Find the task's parent <li> element
                    const taskItem = form.closest('li');

                    // Remove the task from its current section
                    taskItem.remove();

                    // Determine the target section based on the new state
                    const targetList = data.is_active
                        ? document.querySelector('.active-tasks .task-list') // Move to Active Tasks
                        : document.querySelector('.inactive-tasks .task-list-horizontal'); // Move to Suggested Tasks

                    // Append the task to the target section
                    targetList.appendChild(taskItem);

                    // Update the button's appearance
                    const button = form.querySelector('button');
                    button.classList.toggle('active', data.is_active);
                    button.classList.toggle('inactive', !data.is_active);
                } else {
                    alert('Failed to toggle task state.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});