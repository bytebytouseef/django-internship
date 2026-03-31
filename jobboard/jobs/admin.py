from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Job, Application


class ApplicationInline(admin.TabularInline):
    """Inline shows applications nested inside the Job admin page."""
    model = Application
    extra = 0
    readonly_fields = ['applicant', 'applied_at', 'status', 'cover_letter']
    can_delete = False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company_name', 'posted_by', 'job_type',
        'is_active', 'application_count', 'created_at'
    ]
    list_filter = ['job_type', 'experience_level', 'is_active', 'created_at']
    search_fields = ['title', 'company_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ApplicationInline]

    def get_queryset(self, request):
        """
        annotate() adds 'num_applications' to each Job object.
        This is how admin gets the count WITHOUT extra queries per row.
        """
        qs = super().get_queryset(request)
        return qs.annotate(num_applications=Count('applications'))

    # Custom column using the annotated value
    @admin.display(description='Applications', ordering='num_applications')
    def application_count(self, obj):
        count = obj.num_applications
        color = '#28a745' if count > 5 else '#6c757d'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, count
        )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at', 'resume_link']
    list_filter = ['status', 'applied_at']
    search_fields = ['applicant__username', 'job__title', 'cover_letter']
    list_editable = ['status']   # Edit status directly in the list view
    
    def get_queryset(self, request):
        # select_related avoids N+1 in admin list
        return super().get_queryset(request).select_related('job', 'applicant')

    @admin.display(description='Resume')
    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">📄 Download</a>', obj.resume.url)
        return '—'
    