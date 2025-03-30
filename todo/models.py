from django.db import models
from django.contrib.auth.models import User
from desks.models import Desk
from datetime import time

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


class Schedule(models.Model):
    """
    Represents a schedule with a title and multiple moments (day and time).
    """
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class ScheduleMoment(models.Model):
    """
    Represents a specific day and time for a schedule.
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="moments")
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    time_of_day = models.TimeField()

    def __str__(self):
        return f"{self.schedule.title} - {self.get_day_of_week_display()} at {self.time_of_day}"


class Task(models.Model):
    """
    Represents a task that belongs to a category and a desk.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tasks")
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

