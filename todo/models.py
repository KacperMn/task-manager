from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    MODE_CHOICES = [
        ('private', 'Private'),
        ('work', 'Work'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='private')
    workplace = models.ForeignKey('Workplace', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.mode}"


class Workplace(models.Model):
    name = models.CharField(max_length=200)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_workplaces')
    token = models.CharField(max_length=10, unique=True, blank=True)  # Unique token for QR code sharing

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(10)  # Generate a random 10-character token
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    workplace = models.ForeignKey(Workplace, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return f"{self.name} ({self.workplace.name})"