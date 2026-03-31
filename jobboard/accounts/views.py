from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CompanySignUpForm, ApplicantSignUpForm


class CompanySignUpView(CreateView):
    """
    Uses Django's built-in CreateView for form handling.
    Django's authenticate() + login() manage the session.
    """
    form_class = CompanySignUpForm
    template_name = 'accounts/signup_company.html'
    success_url = reverse_lazy('jobs:company_dashboard')

    def form_valid(self, form):
        user = form.save()
        # authenticate() verifies credentials and returns User or None
        # It also sets the user's backend attribute (needed for login())
        user = authenticate(
            username=user.username,
            password=form.cleaned_data['password1']
        )
        if user:
            # login() creates a session and sets request.user
            login(self.request, user)
        messages.success(self.request, f'Welcome, {user.company_name}! Start posting jobs.')
        return redirect(self.success_url)


class ApplicantSignUpView(CreateView):
    form_class = ApplicantSignUpForm
    template_name = 'accounts/signup_applicant.html'
    success_url = reverse_lazy('jobs:job_list')

    def form_valid(self, form):
        user = form.save()
        user = authenticate(
            username=user.username,
            password=form.cleaned_data['password1']
        )
        if user:
            login(self.request, user)
        messages.success(self.request, f'Welcome, {user.get_full_name()}! Find your next role.')
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    """
    Extends Django's built-in LoginView.
    Built-in views handle: form validation, authenticate(), login(), redirect.
    We just override the template.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True  # Redirect if already logged in

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().get_display_name()}!')
        return super().form_valid(form)


def logout_view(request):
    """logout() clears the session and unsets request.user."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('jobs:job_list')