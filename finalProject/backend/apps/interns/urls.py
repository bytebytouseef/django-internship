from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.interns.views import InternViewSet

router = DefaultRouter()
router.register(r'', InternViewSet, basename='interns')

urlpatterns = [
    path('', include(router.urls)),
]
