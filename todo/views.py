from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User  # Add this import
from django.db.models import Q  # Add this import
from django.urls import reverse  # Add this import
from .models import Task, Category, UserProfile, Desk, DeskUserShare
from .utils import generate_unique_slug
from .forms import TaskForm, CategoryForm

def home(request):
    """Redirect authenticated users to their desks list or login page if not authenticated"""
    if request.user.is_authenticated:
        return redirect('desks_list')  # Assuming 'desks_list' is the URL name for my_desks
    return redirect('login')

#------------#
# DESK VIEWS #
#------------#

@login_required
def my_desks(request):
    # Get desks owned by the user
    owned_desks = Desk.objects.filter(user=request.user)
    
    # Get desks shared with the user
    shared_desks = Desk.objects.filter(shared_with=request.user)

    desks = owned_desks | shared_desks
    
    return render(request, 'desk-management/my-desks.html', {
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
        
    return render(request, 'desk-management/create_desk.html')

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
    shared_users = desk.shared_with.all()
    
    return render(request, 'desk-management/edit-desk.html', {
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
    
    return render(request, 'desk-management/share-desk.html', {
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

def get_desk_by_slug(slug, user):
    """Helper function to get a desk by slug and verify ownership or shared access"""
    desk = get_object_or_404(
        Desk, 
        Q(slug=slug) & (Q(user=user) | Q(shared_with=user))  # Owner OR shared user
    )
    return desk

#------------#
# TASK VIEWS #
#------------#
@login_required
def desk_view(request, desk_slug):
    # Use get_desk_by_slug instead of direct query
    desk = get_desk_by_slug(desk_slug, request.user)
    # Optimize with prefetch_related
    tasks = Task.objects.filter(category__desk=desk).select_related('category')
    categories = Category.objects.filter(desk=desk)
    return render(request, 'desk/task-list.html', {
        'desk': desk,
        'tasks': tasks,
        'categories': categories,
        'show_navbar': True,
        'show_footer': True
    })

@login_required
def manage_tasks(request, desk_slug):
    """Manage tasks for a specific desk"""
    desk = get_desk_by_slug(desk_slug, request.user)
    tasks = Task.objects.filter(category__desk=desk)
    categories = Category.objects.filter(desk=desk)
    return render(request, 'desk/manage-tasks.html', {
        'tasks': tasks, 
        'categories': categories,
        'desk': desk,
        'show_navbar': True,
        'show_footer': True
    })

@login_required
def add_task(request, desk_slug):
    desk = get_desk_by_slug(desk_slug, request.user)
    
    if request.method == 'POST':
        form = TaskForm(desk=desk, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # Additional processing if needed
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully.")
            return redirect('tasks_manage', desk_slug=desk_slug)
    else:
        form = TaskForm(desk=desk)
        
    return render(request, 'desk/add_task.html', {
        'form': form,
        'desk': desk,
    })

@login_required
def delete_task(request, desk_slug, task_id):
    """Delete a task from a specific desk"""
    desk = get_desk_by_slug(desk_slug, request.user)
    # Ensure task belongs to this desk
    task = get_object_or_404(Task, id=task_id, category__desk=desk)
    task_title = task.title
    task.delete()
    messages.success(request, f"Task '{task_title}' deleted successfully.")
    return redirect('tasks_manage', desk_slug=desk_slug)

@login_required
def toggle_task_active(request, desk_slug, task_id):
    """Toggle a task's active status on a specific desk"""
    if request.method == 'POST':
        desk = get_desk_by_slug(desk_slug, request.user)
        # Ensure task belongs to this desk
        task = get_object_or_404(Task, id=task_id, category__desk=desk)
        task.is_active = not task.is_active
        task.save()
        status = "completed" if not task.is_active else "active"
        return JsonResponse({
            'success': True, 
            'is_active': task.is_active,
            'message': f"Task marked as {status}."
        })
    return JsonResponse({'success': False}, status=400)

#----------------#
# CATEGORY VIEWS #
#----------------#

@login_required
def manage_categories(request, desk_slug):
    """Manage categories for a specific desk"""
    desk = get_desk_by_slug(desk_slug, request.user)
    categories = Category.objects.filter(desk=desk)
    category_form = CategoryForm()  # Add this line to create a form instance
    
    return render(request, 'desk/manage-categories.html', {
        'categories': categories,
        'desk': desk,
        'form': category_form,  # Pass the form to the template
        'show_navbar': True,
        'show_footer': True
    })

@login_required
def add_category(request, desk_slug):
    """Add a category to a specific desk using CategoryForm"""
    desk = get_desk_by_slug(desk_slug, request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.desk = desk
            category.save()
            messages.success(request, f"Category '{category.title}' created successfully.")
            return redirect('categories_manage', desk_slug=desk_slug)
        else:
            # If the form is not valid, redirect to manage page with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('categories_manage', desk_slug=desk_slug)

    # Redirect to categories_manage for GET requests - you don't need a separate page
    return redirect('categories_manage', desk_slug=desk_slug)

@login_required
def delete_category(request, desk_slug, category_id):
    """Delete a category from a specific desk"""
    desk = get_desk_by_slug(desk_slug, request.user)
    # Ensure category belongs to this desk
    category = get_object_or_404(Category, id=category_id, desk=desk)
    category_title = category.title
    category.delete()
    messages.success(request, f"Category '{category_title}' deleted successfully.")
    return redirect('categories_manage', desk_slug=desk_slug)

#---------------#
# PROFILE VIEWS #
#---------------#

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True
    })
