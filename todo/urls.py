from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

task_patterns = [
    path('', views.todo, name='todo'),
    path('manage-tasks/', views.manage_tasks, name='manage_tasks'),
    path('add/', views.add_task, name='add_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle-active/<int:task_id>/', views.toggle_task_active, name='toggle_task_active'),
]

category_patterns = [
    path('', views.manage_categories, name='manage_categories'),
    path('add/', views.add_category, name='add_category'),
    path('delete/<int:category_id>/', views.delete_category, name='delete_category'),
]

# User-related URLs
user_patterns = [
    path('profile/', views.profile, name='profile'),
    path('workplace/', views.workplace, name='workplace'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/', include((task_patterns, 'tasks'))),
    path('categories/', include((category_patterns, 'categories'))),
    path('select-mode/', views.select_mode, name='select_mode'),
    path('workplace-setup/', views.workplace_setup, name='workplace_setup'),
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('user/', include((user_patterns, 'user'))),  # Add the 'user' namespace
]

urlpatterns += [
    path('logout/', LogoutView.as_view(), name='logout'),
]