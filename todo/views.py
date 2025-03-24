from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Task, Category, UserProfile, Workplace, Role
from .forms import UserRegistrationForm
from django.forms import modelform_factory

# User-related views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('select_mode')  # Redirect to mode selection after registration
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def select_mode(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.mode = mode
        user_profile.save()

        if mode == 'work':
            return redirect('workplace_setup')
        else:
            return redirect('tasks:manage_tasks')

    return render(request, 'select_mode.html')

@login_required
def home(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created or not user_profile.mode:
        return redirect('select_mode')

    if user_profile.mode == 'work' and not user_profile.workplace:
        return redirect('workplace_setup')

    return redirect('tasks:todo')

# Task-related views
@login_required
def todo(request):
    tasks = Task.objects.all()
    categories = Category.objects.all()
    return render(request, 'todo.html', {'tasks': tasks, 'categories': categories})

@login_required
def manage_tasks(request):
    tasks = Task.objects.all()
    categories = Category.objects.all()
    return render(request, 'manage-tasks.html', {'tasks': tasks, 'categories': categories})

@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        if not title or not category_id:
            return HttpResponseBadRequest("Title and category fields are required.")

        category = get_object_or_404(Category, id=category_id)
        Task.objects.create(title=title, description=description, category=category)
        return redirect('tasks:manage_tasks')

    return HttpResponseBadRequest("Invalid request method.")

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('tasks:manage_tasks')

@login_required
def toggle_task_active(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.is_active = not task.is_active
        task.save()
        return JsonResponse({'success': True, 'is_active': task.is_active})
    return JsonResponse({'success': False}, status=400)

# Category-related views
@login_required
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'manage-categories.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not title:
            return HttpResponseBadRequest("All fields are required.")

        Category.objects.create(title=title, description=description)
        return redirect('categories:manage_categories')

    return HttpResponseBadRequest("Invalid request method.")

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('categories:manage_categories')

# Workplace-related views
@login_required
def workplace_setup(request):
    WorkplaceForm = modelform_factory(Workplace, fields=['name'])
    if request.method == 'POST':
        workplace_form = WorkplaceForm(request.POST)
        if workplace_form.is_valid():
            workplace = workplace_form.save(commit=False)
            workplace.manager = request.user
            workplace.save()

            roles = request.POST.getlist('roles')
            for role_name in roles:
                if role_name.strip():
                    Role.objects.create(name=role_name.strip(), workplace=workplace)

            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.workplace = workplace
            user_profile.save()

            return redirect('tasks:manage_tasks')

    workplace_form = WorkplaceForm()
    return render(request, 'workplace_setup.html', {'workplace_form': workplace_form})

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # Update user profile
        mode = request.POST.get('mode')
        if mode in dict(UserProfile.MODE_CHOICES):
            user_profile.mode = mode
            user_profile.save()
        return redirect('user:profile')

    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required
def workplace(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # Update workplace
        workplace_id = request.POST.get('workplace_id')
        if workplace_id:
            try:
                workplace = Workplace.objects.get(id=workplace_id)
                user_profile.workplace = workplace
                user_profile.save()
            except Workplace.DoesNotExist:
                pass
        return redirect('user:workplace')

    workplaces = Workplace.objects.all()  # List all workplaces for selection
    return render(request, 'workplace.html', {'user_profile': user_profile, 'workplaces': workplaces})
