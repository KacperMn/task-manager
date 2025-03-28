import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Desk(models.Model):
    """A desk contains tasks and categories for organization."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_desks')
    shared_with = models.ManyToManyField(User, related_name='shared_desks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Remove unique=True for now
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.name
        
    def get_share_url(self):
        return reverse('accept_desk_share', kwargs={'token': self.share_token})
        
    def refresh_share_token(self):
        self.share_token = uuid.uuid4()
        self.save()
        
    def get_default_permission(self):
        """Get default permission for new users (always view-only)"""
        return 'view'
    
    def share_with_user(self, user, permission=None):
        """Share desk with user using specified permission or default (view)"""
        # If user is desk owner, use owner permission
        if user == self.user:
            permission = 'owner'
        elif permission not in ['view', 'admin']:
            permission = 'view'  # Default for new users
            
        # Create or update share
        share, created = DeskUserShare.objects.update_or_create(
            desk=self,
            user=user,
            defaults={'permission': permission}
        )
        return share

class DeskUserShare(models.Model):
    """Represents a user's access to a desk with specific permission level"""
    PERMISSION_LEVELS = (
        ('view', 'View Only'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    )
    
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='user_shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desk_shares')
    permission = models.CharField(max_length=10, choices=PERMISSION_LEVELS, default='view')
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['desk', 'user']
        
    def get_permission_display(self):
        """Get display name for permission level"""
        for code, name in self.PERMISSION_LEVELS:
            if code == self.permission:
                return name
        return "Unknown"

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

