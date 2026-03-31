from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    
    # Status choices — using Django's choices pattern
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)          # Short text, has a length limit
    body = models.TextField()                          # Long text, no limit
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,                      # Delete posts if user is deleted
        related_name='blog_posts'
    )
    published_date = models.DateTimeField(
        default=timezone.now                           # Defaults to current time
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)   # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)       # Updated on every save

    class Meta:
        ordering = ['-published_date']     # Newest posts first by default

    def __str__(self):
        return self.title                  # How the object appears in Admin & shell