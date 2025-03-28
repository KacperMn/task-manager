from django.shortcuts import get_object_or_404
from django.db.models import Q
from desks.models import Desk, DeskUserShare

def get_desk_by_slug(slug, user):
    """Helper function to get a desk by slug and verify ownership or shared access"""
    # Get desks where user is owner
    desk_query = Q(slug=slug) & Q(user=user)
    
    # OR get desks shared with this user via DeskUserShare
    shared_desk_ids = DeskUserShare.objects.filter(user=user).values_list('desk_id', flat=True)
    if shared_desk_ids:
        desk_query |= Q(slug=slug) & Q(id__in=shared_desk_ids)
    
    desk = get_object_or_404(Desk, desk_query)
    return desk