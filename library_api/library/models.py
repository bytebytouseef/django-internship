from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """
    Represents a book author.
    One author can have many books (one-to-many relationship).
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Book(models.Model):
    """
    Represents a book in the library.
    ForeignKey to Author — many books can belong to one author.
    """
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('self_help', 'Self-Help'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'   # author.books.all() — reverse relation
    )
    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text='13-digit ISBN number'
    )
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default='fiction'
    )
    published_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(2100)
        ]
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} by {self.author.full_name}'