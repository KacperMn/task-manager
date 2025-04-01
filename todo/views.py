from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .utils import toggle_task_status
from .models import Task, Category, UserProfile, Schedule, ScheduleMoment
from .forms import TaskForm, CategoryForm, ScheduleForm, ScheduleMomentFormSet
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
    if request.method == 'POST':
        # Check if it's a schedule form submission
        if 'form_type' in request.POST and request.POST['form_type'] == 'schedule_form':
            schedule_form = ScheduleForm(request.POST)
            moment_formset = ScheduleMomentFormSet(request.POST)

            if schedule_form.is_valid() and moment_formset.is_valid():
                schedule = schedule_form.save()
                moments = moment_formset.save(commit=False)
                for moment in moments:
                    moment.schedule = schedule
                    moment.save()
        # Handle direct task submission from the table form
        else:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            category_id = request.POST.get('category')
            schedule_id = request.POST.get('schedule')
            
            if title and description and category_id:
                category = get_object_or_404(Category, id=category_id, desk=desk)
                task = Task(
                    title=title,
                    description=description,
                    category=category,
                )
                
                # Add schedule if selected
                if schedule_id:
                    task.schedule = get_object_or_404(Schedule, id=schedule_id)
                
                task.save()
                messages.success(request, f"Task '{title}' created successfully.")
                return redirect('tasks_manage', desk_slug=desk.slug)

    else:
        schedule_form = ScheduleForm()
        moment_formset = ScheduleMomentFormSet()

    # Get all schedules
    schedules = Schedule.objects.prefetch_related('moments').all()

    # Get tasks and categories
    tasks = Task.objects.filter(category__desk=desk).select_related('category', 'schedule')
    categories = Category.objects.filter(desk=desk)

    return render(request, 'desk/manage-tasks.html', {
        'tasks': tasks, 
        'categories': categories,
        'desk': desk,
        'schedule_form': schedule_form,
        'moment_formset': moment_formset,
        'schedules': schedules,
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
            # The schedule will be set automatically from the form
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

@get_desk
@login_required
def get_tasks_status(request, desk):
    """Return the current status of all tasks for a desk."""
    tasks = Task.objects.filter(category__desk=desk).values(
        'id', 
        'title', 
        'is_active', 
        'category__id'
    )
    # Add debug information
    return JsonResponse({
        'tasks': list(tasks),
        'timestamp': timezone.now().isoformat(),
        'count': len(tasks)
    })

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

#-----------------#
# SCHEDULE VIEWS #
#-----------------#

@login_required
def delete_schedule(request, schedule_id):
    """Delete a schedule."""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule_name = schedule.title
    schedule.delete()
    messages.success(request, f"Schedule '{schedule_name}' deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'tasks_manage'))

@login_required
def edit_schedule(request, schedule_id):
    """Edit an existing schedule."""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        # Update schedule title
        schedule.title = request.POST.get('title', schedule.title)
        schedule.save()
        
        # Get the count of moments from the form
        moments_count = int(request.POST.get('moments_count', 0))
        
        # Track which moments we've processed
        processed_moment_ids = []
        
        # Update or create moments
        for i in range(moments_count):
            day_of_week = request.POST.get(f'day_of_week_{i}')
            time_of_day = request.POST.get(f'time_of_day_{i}')
            moment_id = request.POST.get(f'moment_id_{i}')
            
            if day_of_week and time_of_day:
                if moment_id:
                    # Update existing moment
                    moment = get_object_or_404(ScheduleMoment, id=moment_id)
                    moment.day_of_week = day_of_week
                    moment.time_of_day = time_of_day
                    moment.save()
                    processed_moment_ids.append(int(moment_id))
                else:
                    # Create new moment
                    moment = ScheduleMoment.objects.create(
                        schedule=schedule,
                        day_of_week=day_of_week,
                        time_of_day=time_of_day
                    )
                    processed_moment_ids.append(moment.id)
        
        # Delete any moments that weren't in the form
        schedule.moments.exclude(id__in=processed_moment_ids).delete()
        
        messages.success(request, f"Schedule '{schedule.title}' updated successfully.")
        return redirect(request.META.get('HTTP_REFERER', 'tasks_manage'))
        
    return HttpResponseBadRequest("Invalid request method")

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
