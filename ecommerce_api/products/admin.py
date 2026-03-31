from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock', 'is_active', 'is_featured']
    list_filter = ['category', 'condition', 'is_active', 'is_featured']
    search_fields = ['name', 'sku']
    list_editable = ['is_active', 'is_featured', 'stock']
    prepopulated_fields = {'slug': ('name',)}