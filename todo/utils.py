from django.shortcuts import get_object_or_404
from django.db.models import Q
from desks.models import Desk, DeskUserShare
from datetime import datetime
from .models import TaskSchedule, TriggerMoment, Task
from .apps import logger

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

def check_schedule_triggers():
    """
    Check all schedule triggers and activate tasks as needed.
    This function runs on a regular schedule via Django Q.
    """
    from django.utils import timezone
    
    # Use Django's timezone-aware now()
    now = timezone.localtime(timezone.now())
    current_day = now.weekday()  # 0=Monday, 6=Sunday
    current_time = now.time().replace(second=0, microsecond=0)  # Round to the minute
    
    # Log for debugging
    logger.info(f"Checking triggers at: {now.strftime('%Y-%m-%d %H:%M')} (Day: {current_day}, Time: {current_time})")
    
    # Find all triggers that match the current day and time
    matching_triggers = TriggerMoment.objects.filter(
        day_of_week=current_day,
        time=current_time
    )
    
    logger.info(f"Found {matching_triggers.count()} matching triggers")
    
    for trigger in matching_triggers:
        template = trigger.template
        # Get all active task schedules using this template
        task_schedules = TaskSchedule.objects.filter(
            template=template,
            is_active=True
        )
        
        logger.info(f"Processing {task_schedules.count()} tasks for template '{template.name}'")
        
        for task_schedule in task_schedules:
            task = task_schedule.task
            desk = template.desk
            
            # Only activate if the task is not already active
            if not task.is_active:
                logger.info(f"Activating task: {task.title}")
                toggle_task_status(task.id, desk)

def apply_schedule_to_task(task, template):
    """
    Apply a schedule template to a task
    
    Args:
        task: Task object to schedule
        template: ScheduleTemplate object to apply
        
    Returns:
        TaskSchedule: The created task schedule object
    """
    
    # Check if this task already has this schedule
    existing = TaskSchedule.objects.filter(task=task, template=template).first()
    if existing:
        # If it exists but is inactive, reactivate it
        if not existing.is_active:
            existing.is_active = True
            existing.save()
        return existing
    
    # Create a new task schedule
    task_schedule = TaskSchedule.objects.create(
        task=task,
        template=template,
        is_active=True
    )
    
    return task_schedule

def remove_schedule_from_task(task, template):
    """
    Remove a schedule template from a task
    
    Args:
        task: Task object
        template: ScheduleTemplate object to remove
        
    Returns:
        bool: True if removed, False if not found
    """
    
    try:
        task_schedule = TaskSchedule.objects.get(task=task, template=template)
        task_schedule.is_active = False
        task_schedule.save()
        return True
    except TaskSchedule.DoesNotExist:
        return False

def setup_scheduled_tasks():
    """
    Set up the scheduled task for checking triggers
    Called after migrations to avoid database access during app initialization
    """
    try:
        from django_q.tasks import schedule
        from django_q.models import Schedule
        
        # Set up the schedule checker to run every minute
        if not Schedule.objects.filter(name='check_schedule_triggers').exists():
            schedule('todo.utils.check_schedule_triggers',
                    schedule_type=Schedule.MINUTES,
                    minutes=1,
                    repeats=-1,
                    name='check_schedule_triggers')
            logger.info("Created schedule for check_schedule_triggers")
    except Exception as e:
        logger.warning(f"Could not set up scheduled tasks: {str(e)}")