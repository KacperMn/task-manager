from django_q.tasks import schedule
from django_q.models import Schedule
from .utils import activate_scheduled_tasks

def schedule_activate_scheduled_tasks():
    if not Schedule.objects.filter(name='Activate Scheduled Tasks').exists():
        schedule(
            'todo.utils.activate_scheduled_tasks',
            name='Activate Scheduled Tasks',
            schedule_type=Schedule.MINUTES,
            minutes=1,
            repeats=-1  # Infinite repeats
        )