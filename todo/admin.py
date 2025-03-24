from django.contrib import admin
from .models import UserProfile, Workplace, Role

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Workplace)
admin.site.register(Role)
