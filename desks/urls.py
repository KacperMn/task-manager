# desks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Desk-related URLs
    path('', views.my_desks, name='desks_list'),
    path('create/', views.create_desk, name='desks_create'),
    path('<int:desk_id>/rename/', views.rename_desk, name='desks_rename'),
    path('<int:desk_id>/delete/', views.delete_desk, name='desks_delete'),
    path('<int:desk_id>/edit/', views.edit_desk, name='desks_edit'),
    path('<int:desk_id>/refresh-token/', views.refresh_desk_token, name='refresh_desk_token'),
    
    # Share-related URLs
    path('<int:desk_id>/share/', views.share_desk, name='share_desk'),
    path('share/<uuid:token>/', views.accept_desk_share, name='accept_desk_share'),
    path('<int:desk_id>/remove-user/<int:user_id>/', views.remove_shared_user, name='remove_shared_user'),
    path('<int:desk_id>/users/<int:user_id>/update-permission/', views.update_user_permission, name='update_user_permission'),
]