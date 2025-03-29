from django.db import models
from django.contrib.auth.models import User
from desks.models import Desk
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Category(models.Model):
    """
    Represents a category for organizing tasks.
    Categories are associated with a specific desk.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Represents a task that belongs to a category and a desk.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tasks")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ScheduleTemplate(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    desk = models.ForeignKey('desks.Desk', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


class TriggerMoment(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    template = models.ForeignKey(ScheduleTemplate, on_delete=models.CASCADE, related_name='triggers')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    time = models.TimeField()
    
    class Meta:
        unique_together = ['template', 'day_of_week', 'time']
        
    def __str__(self):
        return f"{self.get_day_of_week_display()} at {self.time.strftime('%H:%M')}"


class TaskSchedule(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='schedules')
    template = models.ForeignKey(ScheduleTemplate, on_delete=models.CASCADE, related_name='task_schedules')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['task', 'template']

