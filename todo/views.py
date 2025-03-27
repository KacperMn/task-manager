from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, Category, UserProfile, Desk
from .utils import generate_unique_slug
from .forms import TaskForm, CategoryForm  # Update import

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
    desks = Desk.objects.filter(user=request.user)
    return render(request, 'desk-management/my-desks.html', {'desks': desks,})

@login_required
def create_desk(request):
    """Create a new desk for the current user"""
    if request.method == 'POST':
        desk_name = request.POST.get('desk_name')
        if not desk_name:
            messages.error(request, "Desk name is required.")
            return redirect('desks_create')

        # Generate a unique slug for the desk
        slug = generate_unique_slug(desk_name, request.user.id, Desk)

        # Create desk
        desk = Desk.objects.create(
            name=desk_name,
            slug=slug,
            user=request.user
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

#------------#
# TASK VIEWS #
#------------#
@login_required
def desk_view(request, desk_slug):
    desk = get_object_or_404(Desk, slug=desk_slug, user=request.user)
    # Optimize with prefetch_related
    tasks = Task.objects.filter(category__desk=desk).select_related('category')
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
