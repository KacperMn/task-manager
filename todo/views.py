from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from .models import Task, Category

def index(request):
    tasks = Task.objects.all()
    return render(request, 'index.html', {'tasks': tasks})

def manage_tasks(request):
    tasks = Task.objects.all()
    categories = Category.objects.all()
    return render(request, 'manage-tasks.html', {'tasks': tasks, 'categories': categories})

def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'manage-categories.html', {'categories': categories})

def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        if not title or not category_id:
            return HttpResponseBadRequest("Title and category fields are required.")

        category = get_object_or_404(Category, id=category_id)
        Task.objects.create(title=title, description=description, category=category)
        return redirect('manage_tasks')
    else:
        return HttpResponseBadRequest("Invalid request method.")

def edit_task(request, task_id):
    # Logic for editing a task
    pass

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('manage_tasks')

def toggle_task_active(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.is_active = not task.is_active
    task.save()
    return redirect('index')

def add_category(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not title:
            return HttpResponseBadRequest("All fields are required.")

        Category.objects.create(title=title, description=description)
        return redirect('manage_categories')
    else:
        return HttpResponseBadRequest("Invalid request method.")

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('manage_categories')
