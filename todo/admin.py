from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group, User
from .models import UserProfile, Desk

# Unregister the default Group model (optional)
admin.site.unregister(Group)

# Customize the Desk admin
class DeskAdmin(admin.ModelAdmin):
    list_display = ("name", "user")  # Display desk name and associated user
    search_fields = ("name", "user__username")  # Allow searching by desk name or username

# Register the Desk model
admin.site.register(Desk, DeskAdmin)

# Customize the UserProfile admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)  # Display the associated user
    search_fields = ("user__username",)  # Allow searching by username

# Register the UserProfile model
admin.site.register(UserProfile, UserProfileAdmin)

# Extend the default UserAdmin to include only relevant information
class CustomUserAdmin(DefaultUserAdmin):
    def desk(self, obj):
        return obj.desk.name if hasattr(obj, "desk") else "No Desk"

    desk.short_description = "Desk"

    # Customize the list display to show only relevant fields
    list_display = ("username", "email", "desk")

    # Remove unnecessary fields from the form
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
    )

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)