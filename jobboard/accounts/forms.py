from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanySignUpForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm.
    Adds company-specific fields.
    """
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your company name',
            'class': 'form-input',
        })
    )
    company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://yourcompany.com',
            'class': 'form-input',
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'company_name', 'company_website', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        user.company_name = self.cleaned_data['company_name']
        user.company_website = self.cleaned_data.get('company_website', '')
        if commit:
            user.save()
        return user


class ApplicantSignUpForm(UserCreationForm):
    """Standard sign-up form for job seekers."""
    
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-textarea',
            'placeholder': 'Brief professional summary...'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = False
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.bio = self.cleaned_data.get('bio', '')
        if commit:
            user.save()
        return user