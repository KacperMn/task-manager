"""
Utility functions for the Todo application.

This module provides helper functions for desk access control,
task status management, and schedule processing.
"""

# Standard library imports
import logging
from datetime import datetime
from typing import Dict, Optional, Union, List, Tuple, Any

# Django imports
from django.shortcuts import get_object_or_404
from django.db.models import Q, QuerySet
from django.db import transaction
from django.utils import timezone

# Local application imports
from desks.models import Desk, DeskUserShare
from .models import TaskSchedule, TriggerMoment, Task
from .apps import logger

# Constants
TARGET_SECOND = 2  # Schedule checks run at second 02 of each minute


# ======================
# DESK ACCESS FUNCTIONS
# ======================

def get_desk_by_slug(slug: str, user) -> Desk:
    """
    Get a desk by slug and verify ownership or shared access.
    
    Args:
        slug: The desk slug to look up
        user: The user requesting access
        
    Returns:
        Desk object if the user has access
        
    Raises:
        Http404: If desk does not exist or user lacks access
    """
    # Get desks where user is owner
    desk_query = Q(slug=slug) & Q(user=user)
    
    # OR get desks shared with this user via DeskUserShare
    shared_desk_ids = DeskUserShare.objects.filter(user=user).values_list('desk_id', flat=True)
    if shared_desk_ids:
        desk_query |= Q(slug=slug) & Q(id__in=shared_desk_ids)
    
    desk = get_object_or_404(Desk, desk_query)
    return desk


# ===================
# TASK FUNCTIONS 
# ===================

def toggle_task_status(task_id: int, desk: Desk) -> Dict[str, Any]:
    """
    Toggle a task's active status.
    
    Args:
        task_id: ID of the task to toggle
        desk: The desk object the task belongs to
        
    Returns:
        Dictionary containing the updated task and status information
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


# =======================
# SCHEDULING FUNCTIONS
# =======================

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


def remove_schedule_from_task(task: Task, template) -> bool:
    """
    Remove a schedule template from a task.
    
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


def check_schedule_triggers() -> None:
    """
    Check all schedule triggers and activate tasks as needed.
    This function runs on a regular schedule via Django Q.
    """
    from django.utils import timezone
    from django.db import transaction
    
    # Get current time with seconds
    now = timezone.localtime(timezone.now())
    target_second = 2  # Run at second 02
    
    # Only continue if we're at the target second
    if not (target_second - 1 <= now.second <= target_second + 1):
        logger.info(f"Skipping check at second {now.second} (target: {target_second})")
        return
    
    # Normalize time for the minute check (remove seconds)
    current_day = now.weekday()
    current_time = now.time().replace(second=0, microsecond=0)
    
    logger.info(f"Checking triggers at: {now.strftime('%Y-%m-%d %H:%M:%S')} (Day: {current_day}, Time: {current_time})")
    
    # Find matching triggers
    matching_triggers = TriggerMoment.objects.filter(
        day_of_week=current_day,
        time=current_time
    ).select_related('template')
    
    logger.info(f"Found {matching_triggers.count()} matching triggers")
    
    # Direct approach: Find and activate all tasks associated with matching templates
    if matching_triggers.exists():
        template_ids = [trigger.template_id for trigger in matching_triggers]
        
        # Get all tasks that should be activated in one efficient query
        task_schedules = TaskSchedule.objects.filter(
            template_id__in=template_ids,
            is_active=True,
            task__is_active=False  # Only get inactive tasks that need activation
        ).select_related('task')
        
        logger.info(f"Found {task_schedules.count()} tasks to activate")
        
        # Activate all tasks in a single transaction
        with transaction.atomic():
            activated_count = 0
            for schedule in task_schedules:
                task = schedule.task
                task.is_active = True  # Direct activation instead of toggle
                task.save(update_fields=['is_active'])
                activated_count += 1
                logger.info(f"Activated task: {task.title} (ID: {task.id})")
            
            if activated_count > 0:
                logger.info(f"Successfully activated {activated_count} tasks")


# =======================
# SYSTEM SETUP FUNCTIONS
# =======================

def setup_scheduled_tasks() -> None:
    """
    Set up the scheduled task for checking triggers.
    
    Called after migrations to avoid database access during app initialization.
    Creates a Django Q schedule entry to run check_schedule_triggers
    every minute if it doesn't already exist.
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


def list_active_schedules() -> None:
    """
    Helper function to list all active schedules for debugging.
    
    Outputs all active task schedules and their associated triggers
    to the application log.
    """
    now = timezone.localtime(timezone.now())
    
    logger.info(f"=== ACTIVE SCHEDULES AT {now} ===")
    schedules = TaskSchedule.objects.filter(is_active=True).select_related('task', 'template')
    
    for schedule in schedules:
        triggers = TriggerMoment.objects.filter(template=schedule.template)
        logger.info(f"Task: {schedule.task.title} - Template: {schedule.template.name} - "
                   f"Triggers: {triggers.count()}")
        
        for trigger in triggers:
            day_name = dict(TriggerMoment.DAYS_OF_WEEK)[trigger.day_of_week]
            logger.info(f"  - {day_name} at {trigger.time.strftime('%H:%M')}")
    
    logger.info("=== END ACTIVE SCHEDULES ===")