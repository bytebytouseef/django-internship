from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'nationality', 'birth_date', 'book_count']
    search_fields = ['first_name', 'last_name', 'nationality']

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'published_year', 'price', 'rating', 'available']
    list_filter = ['genre', 'available', 'published_year']
    search_fields = ['title', 'isbn', 'author__first_name', 'author__last_name']
    list_editable = ['available']

