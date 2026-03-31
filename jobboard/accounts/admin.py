from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Extend default UserAdmin to show our extra fields."""
    list_display = ['username', 'email', 'company_name', 'is_company', 'is_staff']
    list_filter = ['is_company', 'is_staff', 'is_active']
    
    # Add our custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('is_company', 'company_name', 'company_website', 'bio')
        }),
    )