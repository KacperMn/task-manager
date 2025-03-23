from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('manage-tasks/', views.manage_tasks, name='manage_tasks'),
    path('manage-categories/', views.manage_categories, name='manage_categories'),
    path('add-category/', views.add_category, name='add_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add-task/', views.add_task, name='add_task'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle-task-active/<int:task_id>/', views.toggle_task_active, name='toggle_task_active'),
]