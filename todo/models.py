from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils import timezone

class Desk(models.Model):
    """
    Represents a workspace for tasks and categories.
    Each user will have a personal desk automatically created.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desks')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug based on name and user id
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{self.user.id}"
            
            # Ensure uniqueness
            counter = 1
            while Desk.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{self.user.id}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """
    Represents additional information about a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return self.user.username

    # Remove the desk creation logic from here
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)