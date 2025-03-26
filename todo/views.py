from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.utils.text import slugify
from .models import Task, Category, UserProfile, Desk
from .forms import UserRegistrationForm

# Authentication-related views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'user-handling/register.html', {'form': form})

def home(request):
    """Redirect authenticated users to their first desk or create one if none exists"""
    if request.user.is_authenticated:
        # Try to get first desk for user
        desk = Desk.objects.filter(user=request.user).first()
        
        if not desk:
            # Create a default desk if none exists
            desk_name = "Personal Desk"
            base_slug = slugify(desk_name)
            slug = f"{base_slug}-{request.user.id}"
            # Ensure uniqueness
            counter = 1
            while Desk.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{request.user.id}-{counter}"
                counter += 1
                
            desk = Desk.objects.create(
                name=desk_name,
                slug=slug,
                user=request.user
            )
            # Create a default category
            Category.objects.create(
                title="General",
                description="Default category",
                desk=desk
            )
            messages.success(request, "Your personal desk has been created.")
            
        # Redirect to the tasks list for this desk
        return redirect('tasks_list', desk_slug=desk.slug)
    return redirect('login')


# Desk-related views
@login_required
def my_desks(request):
    desks = Desk.objects.filter(user=request.user)
    return render(request, 'desk-management/my-desks.html', {'desks': desks})

@login_required
def create_desk(request):
    """Create a new desk for the current user"""
    if request.method == 'POST':
        desk_name = request.POST.get('desk_name')
        if not desk_name:
            messages.error(request, "Desk name is required.")
            return redirect('desks_create')
            
        # Generate slug
        base_slug = slugify(desk_name)
        slug = f"{base_slug}-{request.user.id}"
        # Ensure uniqueness
        counter = 1
        while Desk.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{request.user.id}-{counter}"
            counter += 1
            
        # Create desk
        desk = Desk.objects.create(
            name=desk_name,
            slug=slug,
            user=request.user
        )
        
        # Create default category
        Category.objects.create(
            title="General", 
            description="Default category",
            desk=desk
        )
        
        messages.success(request, f"Desk '{desk_name}' created successfully.")
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

def get_desk_by_slug(slug, user):
    """Helper function to get a desk by slug and verify ownership"""
    desk = get_object_or_404(Desk, slug=slug, user=user)
    return desk

# Task-related views
# Rename 'desk' view to 'desk_view' to match URLs
@login_required
def desk_view(request, desk_slug):
    """View tasks for a specific desk identified by slug"""
    desk = get_object_or_404(Desk, slug=desk_slug, user=request.user)
    tasks = Task.objects.filter(category__desk=desk)
    categories = Category.objects.filter(desk=desk)
    return render(request, 'desk/task-list.html', {
        'desk': desk,  # Pass the desk to the template
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
    """Add a task to a specific desk"""
    if request.method == 'POST':
        desk = get_desk_by_slug(desk_slug, request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        
        if not title or not category_id:
            messages.error(request, "Title and category fields are required.")
            return redirect('tasks_manage', desk_slug=desk_slug)
            
        # Verify category belongs to this desk
        category = get_object_or_404(Category, id=category_id, desk=desk)
        Task.objects.create(title=title, description=description, category=category)
        messages.success(request, f"Task '{title}' created successfully.")
        return redirect('tasks_manage', desk_slug=desk_slug)
    return HttpResponseBadRequest("Invalid request method.")

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

# Category-related views
@login_required
def manage_categories(request, desk_slug):
    """Manage categories for a specific desk"""
    desk = get_desk_by_slug(desk_slug, request.user)
    categories = Category.objects.filter(desk=desk)
    return render(request, 'desk/manage-categories.html', {
        'categories': categories,
        'desk': desk,
        'show_navbar': True,
        'show_footer': True
    })

@login_required
def add_category(request, desk_slug):
    """Add a category to a specific desk"""
    if request.method == 'POST':
        desk = get_desk_by_slug(desk_slug, request.user)
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if not title:
            messages.error(request, "Category title is required.")
            return redirect('categories_manage', desk_slug=desk_slug)
            
        Category.objects.create(title=title, description=description, desk=desk)
        messages.success(request, f"Category '{title}' created successfully.")
        return redirect('categories_manage', desk_slug=desk_slug)
    return HttpResponseBadRequest("Invalid request method.")

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

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        mode = request.POST.get('mode')
        if mode in dict(UserProfile.MODE_CHOICES):
            user_profile.mode = mode
            user_profile.save()
        return redirect('user_profile')
    return render(request, 'user-handling/profile.html', {'user_profile': user_profile})
