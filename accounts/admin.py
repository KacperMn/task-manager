from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group, User

admin.site.unregister(Group)

# For User admin customization
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ("username", "email")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)