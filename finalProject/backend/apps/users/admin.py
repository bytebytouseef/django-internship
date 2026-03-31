from django.contrib import admin
from apps.users.models import User
from apps.interns.models import Intern
from apps.assignments.models import Assignment, AssignmentSubmission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_admin', 'created_at']
    list_filter = ['is_admin', 'created_at']
    search_fields = ['email', 'username']

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'department', 'start_date', 'end_date']
    list_filter = ['department', 'start_date']
    search_fields = ['full_name', 'email']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'due_date']
    search_fields = ['title', 'assigned_to__full_name']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'submitted_by', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['assignment__title', 'submitted_by__full_name']
