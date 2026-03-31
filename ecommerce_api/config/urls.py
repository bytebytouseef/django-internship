from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── API v1 — URLPathVersioning ──
    # URLPathVersioning: version is part of the URL path
    # /api/v1/products/, /api/v2/products/
    # DRF reads request.version from the URL
    path('api/v1/', include([
        path('', include('accounts.urls')),
        path('', include('products.urls')),
        path('', include('orders.urls')),
    ])),

    # ── drf-spectacular: OpenAPI Schema & Swagger UI ──
    # SpectacularAPIView: generates the raw OpenAPI JSON/YAML schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # SpectacularSwaggerView: interactive Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # SpectacularRedocView: alternative ReDoc documentation UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Browsable API login
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)