import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Desk(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    share_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate a slug if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Desk.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
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
    """Represents a user's access to a shared desk with specific permission level"""
    PERMISSION_CHOICES = (
        ('view', 'View Only'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    )
    
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='user_shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='desk_shares')
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['desk', 'user']
