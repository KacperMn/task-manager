from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .utils import toggle_task_status
from .models import Task, Category, UserProfile
from .forms import TaskForm, CategoryForm
from .decorators import get_desk

def home(request):
    """Redirect authenticated users to their desks list or login page if not authenticated"""
    if request.user.is_authenticated:
        return redirect('desks_list')
    return redirect('login')

#------------#
# TASK VIEWS #
#------------#

@get_desk
@login_required
def desk_view(request, desk):
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

@get_desk
@login_required
def manage_tasks(request, desk):
    """Manage tasks for a specific desk"""
    tasks = Task.objects.filter(category__desk=desk)
    categories = Category.objects.filter(desk=desk)
    return render(request, 'desk/manage-tasks.html', {
        'tasks': tasks, 
        'categories': categories,
        'desk': desk,
        'show_navbar': True,
        'show_footer': True
    })

@get_desk
@login_required
def add_task(request, desk):
    
    if request.method == 'POST':
        form = TaskForm(desk=desk, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully.")
            return redirect('tasks_manage', desk_slug=desk.slug)
    else:
        form = TaskForm(desk=desk)
        
    return render(request, 'desk/add_task.html', {
        'form': form,
        'desk': desk,
    })

@get_desk
@login_required
def delete_task(request, desk, task_id):
    """Delete a task from a specific desk"""
    task = get_object_or_404(Task, id=task_id, category__desk=desk)
    task_title = task.title
    task.delete()
    messages.success(request, f"Task '{task_title}' deleted successfully.")
    return redirect('tasks_manage', desk_slug=desk.slug)

@get_desk
@login_required
def toggle_task_status_manual(request, desk, task_id):
    """Toggle a task's active status on a specific desk"""
    if request.method == 'POST':
        result = toggle_task_status(task_id, desk)
        return JsonResponse({
            'success': True, 
            'is_active': result['is_active'],
            'message': f"Task marked as {result['status']}."
        })
    return JsonResponse({'success': False}, status=400)

#----------------#
# CATEGORY VIEWS #
#----------------#

@get_desk
@login_required
def manage_categories(request, desk):
    """Manage categories for a specific desk"""
    categories = Category.objects.filter(desk=desk)
    category_form = CategoryForm()  # Add this line to create a form instance
    
    return render(request, 'desk/manage-categories.html', {
        'categories': categories,
        'desk': desk,
        'form': category_form,  # Pass the form to the template
        'show_navbar': True,
        'show_footer': True
    })


@get_desk
@login_required
def add_category(request, desk):
    """Add a category to a specific desk using CategoryForm"""
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.desk = desk
            category.save()
            messages.success(request, f"Category '{category.title}' created successfully.")
            return redirect('categories_manage', desk_slug=desk.slug)
        else:
            # If the form is not valid, redirect to manage page with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('categories_manage', desk_slug=desk.slug)

    # Redirect to categories_manage for GET requests - you don't need a separate page
    return redirect('categories_manage', desk_slug=desk.slug)

@get_desk
@login_required
def delete_category(request, desk, category_id):
    """Delete a category from a specific desk"""
    category = get_object_or_404(Category, id=category_id, desk=desk)
    category_title = category.title
    category.delete()
    messages.success(request, f"Category '{category_title}' deleted successfully.")
    return redirect('categories_manage', desk_slug=desk.slug)

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
