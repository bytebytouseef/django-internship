from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # All API endpoints under /api/
    path('api/', include('library.urls')),

    # DRF's built-in login/logout for the Browsable API
    # Enables the "Log in" button on the browsable interface
    path('api-auth/', include('rest_framework.urls')),
]