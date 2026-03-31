from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Post


def post_list(request):
    """
    List view — shows all PUBLISHED posts.
    Demonstrates: QuerySet API, filtering, ordering
    """
    # ORM QuerySet — filter() returns posts with status='published'
    # order_by() overrides Meta ordering (though they match here)
    posts = Post.objects.filter(status='published').order_by('-published_date')
    
    # count() and exists() — useful QuerySet methods
    total_posts = posts.count()
    has_posts = posts.exists()
    
    # Context dict — passed to template as variables
    context = {
        'posts': posts,
        'total_posts': total_posts,
        'has_posts': has_posts,
        'page_title': 'Latest Posts',
    }
    
    # render() combines: template + context → HttpResponse
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    """
    Detail view — shows a single post.
    Demonstrates: get_object_or_404, field lookups
    """
    # get_object_or_404 — returns 404 page if not found instead of crashing
    # Looks up by primary key AND status=published (both conditions must match)
    post = get_object_or_404(Post, pk=pk, status='published')
    
    # QuerySet examples — related posts by same author
    related_posts = Post.objects.filter(
        author=post.author,
        status='published'
    ).exclude(pk=pk).order_by('-published_date')[:3]  # exclude current, limit to 3
    
    # Flash message example
    # messages.success(request, 'Post loaded successfully!')
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'page_title': post.title,
    }
    
    return render(request, 'blog/post_detail.html', context)