from django.shortcuts import get_object_or_404
from django.db.models import Q
from desks.models import Desk, DeskUserShare
from datetime import datetime
from .models import Task
import logging

logger = logging.getLogger(__name__)

def get_desk_by_slug(slug, user):
    """Helper function to get a desk by slug and verify ownership or shared access"""
    # Get desks where user is owner
    desk_query = Q(slug=slug) & Q(user=user)
    
    # OR get desks shared with this user via DeskUserShare
    shared_desk_ids = DeskUserShare.objects.filter(user=user).values_list('desk_id', flat=True)
    if shared_desk_ids:
        desk_query |= Q(slug=slug) & Q(id__in=shared_desk_ids)
    
    desk = get_object_or_404(Desk, desk_query)
    return desk

def toggle_task_status(task_id, desk):
    """
    Toggle a task's active status
    
    Args:
        task_id: ID of the task to toggle
        desk: The desk object the task belongs to
        
    Returns:
        dict: Dictionary containing the updated task and status information
    """
    task = get_object_or_404(Task, id=task_id, category__desk=desk)
    task.is_active = not task.is_active
    task.save()
    status = "completed" if not task.is_active else "active"
    
    return {
        'task': task,
        'is_active': task.is_active,
        'status': status
    }

def activate_scheduled_tasks():
    """
    Activates tasks whose schedule moments match the current day and time.
    """
    logger.info("Running activate_scheduled_tasks...")
    now = datetime.now()
    current_day = now.weekday()  # Monday is 0, Sunday is 6
    current_time = now.time()

    # Find tasks with matching schedule moments
    tasks_to_activate = Task.objects.filter(
        schedule__moments__day_of_week=current_day,
        schedule__moments__time_of_day__lte=current_time,
        is_active=False
    ).distinct()

    # Activate each task using toggle_task_status
    for task in tasks_to_activate:
        try:
            toggle_task_status(task.id, task.category.desk)
            logger.info(f"Activated task {task.id}")
        except Exception as e:
            # Log the error
            logger.error(f"Error activating task {task.id}: {e}")