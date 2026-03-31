from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/company/', views.CompanySignUpView.as_view(), name='signup_company'),
    path('signup/applicant/', views.ApplicantSignUpView.as_view(), name='signup_applicant'),
]