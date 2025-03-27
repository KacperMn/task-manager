from django.contrib import admin
from .models import Task, Category, Desk, UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)  # Removed 'mode' field

class DeskAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

class TaskAdmin(admin.ModelAdmin):
    # Adjusting list_display to use fields that exist on Task model
    list_display = ('title', 'category', 'is_active')  # Removed 'created_at' if it doesn't exist

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Desk, DeskAdmin)
admin.site.register(Category)
admin.site.register(Task, TaskAdmin)