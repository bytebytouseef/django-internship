from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    
    # Columns shown in the list view
    list_display = ['title', 'author', 'status', 'published_date', 'created_at']
    
    # Sidebar filters
    list_filter = ['status', 'published_date', 'author']
    
    # Search bar — searches these fields
    search_fields = ['title', 'body']
    
    # Default ordering in admin
    ordering = ['-published_date']
    
    # Prepopulate slug if you add one later
    # prepopulated_fields = {'slug': ('title',)}