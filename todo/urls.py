from django.urls import path
from . import views

urlpatterns = [
    # Home URL
    path('', views.home, name='home'),

    # Task-related URLs with desk slug
    path('<slug:desk_slug>/', views.desk_view, name='tasks_list'),
    path('<slug:desk_slug>/manage-tasks/', views.manage_tasks, name='tasks_manage'),
    path('<slug:desk_slug>/add-task/', views.add_task, name='tasks_add'),
    path('<slug:desk_slug>/delete-task/<int:task_id>/', views.delete_task, name='tasks_delete'),
    path('<slug:desk_slug>/toggle-task-status/<int:task_id>/', views.toggle_task_status_manual, name='tasks_toggle'),

    # Category-related URLs with desk slug
    path('<slug:desk_slug>/manage-categories/', views.manage_categories, name='categories_manage'),
    path('<slug:desk_slug>/add-category/', views.add_category, name='categories_add'),
    path('<slug:desk_slug>/delete-category/<int:category_id>/', views.delete_category, name='categories_delete'),
    
    # User-related URLs
    path('user/profile/', views.profile, name='user_profile'),
]