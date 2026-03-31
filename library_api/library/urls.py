from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# ============================================================
# DefaultRouter — auto-generates URL patterns for ViewSets
#
# For AuthorViewSet, it generates:
#   GET    /authors/          → AuthorViewSet.list()
#   POST   /authors/          → AuthorViewSet.create()
#   GET    /authors/{pk}/     → AuthorViewSet.retrieve()
#   PUT    /authors/{pk}/     → AuthorViewSet.update()
#   PATCH  /authors/{pk}/     → AuthorViewSet.partial_update()
#   DELETE /authors/{pk}/     → AuthorViewSet.destroy()
#
# DefaultRouter also adds:
#   GET /  → API root with hyperlinks to all registered endpoints
#
# SimpleRouter — same as DefaultRouter but WITHOUT the API root view
# ============================================================

router = DefaultRouter()

# register(prefix, viewset, basename)
# prefix = URL prefix ('authors' → /authors/ and /authors/{pk}/)
# basename = used to generate URL names (authors-list, authors-detail)
router.register(r'authors', views.AuthorViewSet, basename='author')
router.register(r'books', views.BookViewSet, basename='book')

urlpatterns = [
    # All ViewSet URLs from the router
    path('', include(router.urls)),

    # Function-based API views
    path('overview/', views.api_overview, name='api-overview'),
    path('stats/', views.api_stats, name='api-stats'),
    path('search/', views.search_books, name='search-books'),

    # Manual APIView example
    path('books-manual/', views.ManualBookListView.as_view(), name='books-manual'),

    # Generic view example
    path('books-generic/', views.BookListCreateGenericView.as_view(), name='books-generic'),

    # ── AUTHENTICATION ENDPOINTS ──

    # obtain_auth_token — built-in DRF view
    # POST with username + password → returns {"token": "abc123..."}
    path('auth/token/', obtain_auth_token, name='api-token'),

    # Our custom register view
    path('auth/register/', views.register_user, name='api-register'),
]