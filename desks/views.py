from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Desk, DeskUserShare
from .utils import generate_unique_slug
from django.http import HttpResponseBadRequest
from todo.models import Category, Task

@login_required
def my_desks(request):
    # Get desks owned by the user
    owned_desks = Desk.objects.filter(user=request.user)
    
    # Get desks shared with the user via DeskUserShare
    shared_desk_ids = DeskUserShare.objects.filter(user=request.user).values_list('desk_id', flat=True)
    shared_desks = Desk.objects.filter(id__in=shared_desk_ids)

    # Combine the querysets (owned + shared)
    desks = owned_desks | shared_desks
    
    return render(request, 'my-desks.html', {
        'owned_desks': owned_desks,
        'shared_desks': shared_desks,
        'desks': desks
    })

@login_required
def create_desk(request):
    """Create a new desk for the current user"""
    if request.method == 'POST':
        desk_name = request.POST.get('desk_name')
        visibility = request.POST.get('visibility', 'private')
        
        if not desk_name:
            messages.error(request, "Desk name is required.")
            return redirect('desks_create')

        # Generate a unique slug for the desk
        slug = generate_unique_slug(desk_name, request.user.id, Desk)

        # Create desk with a share token
        desk = Desk.objects.create(
            name=desk_name,
            slug=slug,
            user=request.user
        )
        
        messages.success(request, f"Desk '{desk_name}' created successfully.")
        
        # If public desk, redirect to sharing page
        if visibility == 'public':
            return redirect('share_desk', desk_id=desk.id)
        
        # Otherwise go to the desk itself
        return redirect('tasks_list', desk_slug=desk.slug)
        
    return render(request, 'create_desk.html')

@login_required
def rename_desk(request, desk_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if not new_name:
            return HttpResponseBadRequest("New name is required.")
        desk = get_object_or_404(Desk, id=desk_id, user=request.user)
        desk.name = new_name
        desk.save()
        return redirect('desks_list')
    return HttpResponseBadRequest("Invalid request method.")

@login_required
def delete_desk(request, desk_id):
    if request.method == 'POST':
        desk = get_object_or_404(Desk, id=desk_id, user=request.user)
        desk.delete()
        return redirect('desks_list')
    return HttpResponseBadRequest("Invalid request method.")

@login_required
def edit_desk(request, desk_id):
    desk = get_object_or_404(Desk, id=desk_id, user=request.user)
    
    if request.method == 'POST':
        new_name = request.POST.get('desk_name')
        description = request.POST.get('desk_description', '')
        
        if not new_name:
            messages.error(request, "Desk name is required")
            return redirect('desks_edit', desk_id=desk_id)
            
        desk.name = new_name
        desk.description = description  # You'll need to add this field to your Desk model
        desk.save()
        messages.success(request, f"Desk '{desk.name}' updated successfully")
        return redirect('desks_list')
    
    # Get additional data for the template
    categories = Category.objects.filter(desk=desk)
    tasks_count = Task.objects.filter(category__desk=desk).count()
    
    # Get users who have access to this desk
    shared_user_ids = DeskUserShare.objects.filter(desk=desk).values_list('user_id', flat=True)
    shared_users = User.objects.filter(id__in=shared_user_ids)
    
    return render(request, 'edit-desk.html', {
        'desk': desk,
        'categories': categories,
        'tasks_count': tasks_count,
        'shared_users': shared_users
    })

@login_required
def refresh_desk_token(request, desk_id):
    """Generate a new share token for a desk"""
    if request.method == 'POST':
        desk = get_object_or_404(Desk, id=desk_id, user=request.user)
        desk.refresh_share_token()
        messages.success(request, "New share link generated successfully")
    return redirect('desks_edit', desk_id=desk_id)

@login_required
def accept_desk_share(request, token):
    """Accept a shared desk via token"""
    try:
        desk = get_object_or_404(Desk, share_token=token)
        
        # Check if user is already the owner
        if desk.user == request.user:
            messages.info(request, "You already own this desk")
            return redirect('tasks_list', desk_slug=desk.slug)
            
        # Share with the user using view permission by default
        share = desk.share_with_user(request.user)
        messages.success(request, f"You now have access to '{desk.name}' desk")
            
        return redirect('tasks_list', desk_slug=desk.slug)
        
    except Exception as e:
        messages.error(request, "Invalid or expired share link")
        return redirect('home')

@login_required
def remove_shared_user(request, desk_id, user_id):
    """Remove a user's access to a shared desk"""
    if request.method == 'POST':
        desk = get_object_or_404(Desk, id=desk_id, user=request.user)
        user_to_remove = get_object_or_404(User, id=user_id)
        
        # Cannot remove the owner
        if user_to_remove == desk.user:
            messages.error(request, "Cannot remove the owner from their own desk")
            return redirect('share_desk', desk_id=desk_id)
        
        # Delete the share
        DeskUserShare.objects.filter(desk=desk, user=user_to_remove).delete()
        messages.success(request, f"Access for {user_to_remove.username} has been removed")
    return redirect('share_desk', desk_id=desk_id)

@login_required
def share_desk(request, desk_id):
    """Display sharing options for a desk"""
    desk = get_object_or_404(Desk, id=desk_id, user=request.user)
    
    # Get all user shares (excluding owner)
    user_shares = DeskUserShare.objects.filter(desk=desk).exclude(user=desk.user).select_related('user')
    
    # Create the full share URL
    share_url = request.build_absolute_uri(
        reverse('accept_desk_share', kwargs={'token': desk.share_token})
    )
    
    return render(request, 'share-desk.html', {
        'desk': desk,
        'user_shares': user_shares,
        'share_url': share_url
    })

@login_required
def update_user_permission(request, desk_id, user_id):
    """Update a user's permission level for a shared desk"""
    if request.method == 'POST':
        desk = get_object_or_404(Desk, id=desk_id, user=request.user)
        user_to_update = get_object_or_404(User, id=user_id)
        new_permission = request.POST.get('permission')
        
        # Validate permission value
        if new_permission not in ['view', 'admin']:
            messages.error(request, "Invalid permission level")
            return redirect('share_desk', desk_id=desk_id)
        
        # Get the share and update it
        share = get_object_or_404(DeskUserShare, desk=desk, user=user_to_update)
        
        # Don't allow changing owner permission
        if share.permission == 'owner':
            messages.error(request, "Cannot change the owner's permission level")
            return redirect('share_desk', desk_id=desk_id)
        
        share.permission = new_permission
        share.save()
        
        messages.success(request, f"Updated {user_to_update.username}'s permission to {share.get_permission_display()}")
    return redirect('share_desk', desk_id=desk_id)