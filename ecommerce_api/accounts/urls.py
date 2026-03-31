from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('auth/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/token/verify/', views.CustomTokenVerifyView.as_view(), name='token-verify'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
]