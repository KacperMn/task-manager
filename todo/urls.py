from django.urls import path
from . import views

urlpatterns = [
    # Home URL
    path('', views.home, name='home'),

    # Desk-related URLs
    path('my-desks/', views.my_desks, name='desks_list'),
    path('my-desks/create/', views.create_desk, name='desks_create'),
    path('my-desks/<int:desk_id>/rename/', views.rename_desk, name='desks_rename'),
    path('my-desks/<int:desk_id>/delete/', views.delete_desk, name='desks_delete'),
    path('my-desks/<int:desk_id>/edit/', views.edit_desk, name='desks_edit'),
    path('my-desks/<int:desk_id>/refresh-token/', views.refresh_desk_token, name='refresh_desk_token'),

    # Task-related URLs with desk slug
    path('my-desks/<slug:desk_slug>/', views.desk_view, name='tasks_list'),
    path('my-desks/<slug:desk_slug>/manage-tasks/', views.manage_tasks, name='tasks_manage'),
    path('my-desks/<slug:desk_slug>/add-task/', views.add_task, name='tasks_add'),
    path('my-desks/<slug:desk_slug>/delete-task/<int:task_id>/', views.delete_task, name='tasks_delete'),
    path('my-desks/<slug:desk_slug>/toggle-task-active/<int:task_id>/', views.toggle_task_active, name='tasks_toggle'),

    # Share-related URLs
    path('my-desks/<int:desk_id>/share/', views.share_desk, name='share_desk'),
    path('my-desks/share/<uuid:token>/', views.accept_desk_share, name='accept_desk_share'),
    path('my-desks/<int:desk_id>/remove-user/<int:user_id>/', views.remove_shared_user, name='remove_shared_user'),
    path('my-desks/<int:desk_id>/users/<int:user_id>/update-permission/', views.update_user_permission, name='update_user_permission'),

    # Category-related URLs with desk slug
    path('my-desks/<slug:desk_slug>/manage-categories/', views.manage_categories, name='categories_manage'),
    path('my-desks/<slug:desk_slug>/add-category/', views.add_category, name='categories_add'),
    path('my-desks/<slug:desk_slug>/delete-category/<int:category_id>/', views.delete_category, name='categories_delete'),
    
    # User-related URLs
    path('user/profile/', views.profile, name='user_profile'),
]