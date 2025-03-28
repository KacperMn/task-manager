from django.utils.text import slugify
from todo.models import DeskUserShare

def generate_unique_slug(base_name, user_id, model_class):
    """Generate a unique slug based on name and user_id."""
    base_slug = slugify(base_name)
    slug = f"{base_slug}-{user_id}"
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{user_id}-{counter}"
        counter += 1
    return slug

def get_user_desk_permissions(user, desk):
    """
    Get a user's permissions for a desk
    Returns a dict with can_view, can_edit, is_admin permissions
    """
    # Owner has all permissions
    if desk.user == user:
        return {
            'can_view': True,
            'can_edit': True, 
            'is_admin': True,
            'is_owner': True
        }
    
    # Get the user's share
    try:
        share = DeskUserShare.objects.get(desk=desk, user=user)
        permission = share.permission
        
        if permission == 'admin':
            return {
                'can_view': True,
                'can_edit': True,
                'is_admin': True,
                'is_owner': False
            }
        elif permission == 'view':
            return {
                'can_view': True,
                'can_edit': False,
                'is_admin': False,
                'is_owner': False
            }
    except DeskUserShare.DoesNotExist:
        # No permissions
        pass
        
    return {
        'can_view': False,
        'can_edit': False,
        'is_admin': False,
        'is_owner': False
    }