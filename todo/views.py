from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .utils import toggle_task_status, apply_schedule_to_task, remove_schedule_from_task
from .models import Task, Category, UserProfile, ScheduleTemplate, TriggerMoment, TaskSchedule
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
def manage_tasks(request, desk):
    """View to manage tasks for a specific desk"""
    tasks = Task.objects.filter(category__desk=desk).select_related('category').prefetch_related('schedules__template')
    categories = Category.objects.filter(desk=desk)
    schedule_templates = ScheduleTemplate.objects.filter(desk=desk)
    
    # Current template being worked on
    current_template = None
    triggers = []
    
    # If we're editing a template, get its triggers
    template_id = request.session.get('current_template_id')
    if template_id:
        try:
            current_template = ScheduleTemplate.objects.get(id=template_id, desk=desk)
            triggers = TriggerMoment.objects.filter(template=current_template)
        except ScheduleTemplate.DoesNotExist:
            # Clear invalid template ID
            if 'current_template_id' in request.session:
                del request.session['current_template_id']
    
    context = {
        'desk': desk,
        'tasks': tasks,
        'categories': categories,
        'schedule_templates': schedule_templates,
        'days_of_week': TriggerMoment.DAYS_OF_WEEK,
        'TIME_ZONE': settings.TIME_ZONE,
        'current_template': current_template,
        'triggers': triggers,
        'show_navbar': True,
        'show_footer': True
    }
    return render(request, 'desk/manage-tasks.html', context)

@get_desk
@login_required
@require_http_methods(["POST"])
def create_template(request, desk):
    """Create or update schedule template"""
    
    # Handle adding a trigger to a template
    if 'add_trigger' in request.POST:
        day = request.POST.get('day')
        time = request.POST.get('time')
        
        template_id = request.session.get('current_template_id')
        
        # If no template exists or stored template doesn't exist, create one
        if not template_id or not ScheduleTemplate.objects.filter(id=template_id, desk=desk).exists():
            template_name = request.POST.get('name')
            if not template_name:
                # Need a name to create a new template
                return redirect('tasks_manage', desk_slug=desk.slug)
                
            template = ScheduleTemplate.objects.create(
                name=template_name,
                user=request.user,
                desk=desk
            )
            request.session['current_template_id'] = template.id
        else:
            template = ScheduleTemplate.objects.get(id=template_id)
        
        # Add the trigger
        if day and time:
            TriggerMoment.objects.create(
                template=template,
                day_of_week=day,
                time=time
            )
        
        return redirect('tasks_manage', desk_slug=desk.slug)
    
    # Handle saving the template (finish editing)
    elif 'save_template' in request.POST:
        template_id = request.session.get('current_template_id')
        
        # If there's no current template, create one
        if not template_id or not ScheduleTemplate.objects.filter(id=template_id, desk=desk).exists():
            name = request.POST.get('name')
            if name:
                ScheduleTemplate.objects.create(
                    name=name,
                    user=request.user,
                    desk=desk
                )
        
        # Clear the session
        if 'current_template_id' in request.session:
            del request.session['current_template_id']
        
        return redirect('tasks_manage', desk_slug=desk.slug)
    
    return redirect('tasks_manage', desk_slug=desk.slug)

@get_desk
@login_required
def remove_trigger(request, desk, trigger_id):
    """Remove a trigger from a template"""
    trigger = get_object_or_404(TriggerMoment, id=trigger_id, template__desk=desk)
    trigger.delete()
    
    return redirect('tasks_manage', desk_slug=desk.slug)

@get_desk
@login_required
@require_http_methods(["POST"])
def apply_template(request, desk):
    """Apply a schedule template to a task"""
    template_id = request.POST.get('template_id')
    task_id = request.POST.get('task_id')
    
    if not template_id or not task_id:
        return redirect('tasks_manage', desk_slug=desk.slug)
    
    template = get_object_or_404(ScheduleTemplate, id=template_id, desk=desk)
    task = get_object_or_404(Task, id=task_id, category__desk=desk)
    
    # Apply the schedule template to the task
    apply_schedule_to_task(task, template)
    
    return redirect('tasks_manage', desk_slug=desk.slug)

@get_desk
@login_required
def remove_schedule(request, desk, task_id, schedule_id):
    """Remove a schedule from a task"""
    task = get_object_or_404(Task, id=task_id, category__desk=desk)
    schedule = get_object_or_404(TaskSchedule, id=schedule_id, task=task)
    
    # Mark the schedule as inactive
    schedule.is_active = False
    schedule.save()
    
    return redirect('tasks_manage', desk_slug=desk.slug)

@get_desk
@login_required
def delete_template(request, desk, template_id):
    """Delete a schedule template"""
    template = get_object_or_404(ScheduleTemplate, id=template_id, desk=desk)
    template.delete()
    
    return redirect('tasks_manage', desk_slug=desk.slug)

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
