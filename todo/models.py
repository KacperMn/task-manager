from django.db import models
from django.contrib.auth.models import User
from desks.models import Desk

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

