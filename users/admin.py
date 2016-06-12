from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')
    fields = ('username', 'email', 'is_active', 'is_staff', 'date_joined', 'last_login')


admin.site.register(User, UserAdmin)
