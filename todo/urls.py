from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Home URL
    path('', views.home, name='home'),

    # Desk-related URLs
    path('my-desks/', views.my_desks, name='desks_list'),
    path('my-desks/create/', views.create_desk, name='desks_create'),
    path('my-desks/<int:desk_id>/rename/', views.rename_desk, name='desks_rename'),
    path('my-desks/<int:desk_id>/delete/', views.delete_desk, name='desks_delete'),

    # Task-related URLs with desk slug
    path('my-desks/<slug:desk_slug>/', views.desk_view, name='tasks_list'),
    path('my-desks/<slug:desk_slug>/manage-tasks/', views.manage_tasks, name='tasks_manage'),
    path('my-desks/<slug:desk_slug>/add-task/', views.add_task, name='tasks_add'),
    path('my-desks/<slug:desk_slug>/delete-task/<int:task_id>/', views.delete_task, name='tasks_delete'),
    path('my-desks/<slug:desk_slug>/toggle-task-active/<int:task_id>/', views.toggle_task_active, name='tasks_toggle'),

    # Category-related URLs with desk slug
    path('my-desks/<slug:desk_slug>/manage-categories/', views.manage_categories, name='categories_manage'),
    path('my-desks/<slug:desk_slug>/add-category/', views.add_category, name='categories_add'),
    path('my-desks/<slug:desk_slug>/delete-category/<int:category_id>/', views.delete_category, name='categories_delete'),
    
    # User-related URLs
    path('user/profile/', views.profile, name='user_profile'),
]