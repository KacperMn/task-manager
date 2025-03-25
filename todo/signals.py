from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, Desk

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile whenever a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
        Desk.objects.create(user=instance)