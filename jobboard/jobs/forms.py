from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Job, Application
import os

User = get_user_model()


# ============================================================
# CUSTOM VALIDATORS
# ============================================================

def validate_pdf_or_doc(value):
    """
    Custom validator — called automatically during form validation.
    Raises ValidationError to reject invalid input.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext not in valid_extensions:
        raise ValidationError(
            f'Only PDF and Word documents are allowed. You uploaded: {ext}'
        )


def validate_file_size(value):
    """Reject files larger than 5MB."""
    limit = 5 * 1024 * 1024  # 5MB in bytes
    if value.size > limit:
        raise ValidationError('File too large. Maximum size is 5MB.')


# ============================================================
# forms.ModelForm — auto-generates fields from a Model
# ============================================================

class JobPostForm(forms.ModelForm):
    """
    ModelForm: automatically creates form fields matching the model.
    We override some widgets for better UX.
    """
    
    class Meta:
        model = Job
        # Exclude auto-set fields
        exclude = ['posted_by', 'created_at', 'updated_at']
        
        # Widget overrides — change how fields render in HTML
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Senior Python Developer',
                'class': 'form-input',
            }),
            'company_name': forms.TextInput(attrs={
                'placeholder': 'Your company name',
                'class': 'form-input',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. New York, NY or Remote',
                'class': 'form-input',
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities...',
                'class': 'form-textarea',
            }),
            'requirements': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Required skills, qualifications...',
                'class': 'form-textarea',
            }),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'salary_min': forms.NumberInput(attrs={
                'placeholder': 'e.g. 60000',
                'class': 'form-input',
            }),
            'salary_max': forms.NumberInput(attrs={
                'placeholder': 'e.g. 90000',
                'class': 'form-input',
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    # ─── FIELD-LEVEL VALIDATION ───
    # clean_<fieldname>() is called automatically for each field
    
    def clean_title(self):
        """Field-level validator for 'title'."""
        title = self.cleaned_data.get('title', '')
        if len(title) < 5:
            raise ValidationError('Job title must be at least 5 characters.')
        # Return cleaned value — always return from clean_<field>
        return title.strip()
    
    def clean_salary_min(self):
        """Ensure salary_min is positive."""
        salary_min = self.cleaned_data.get('salary_min')
        if salary_min is not None and salary_min < 0:
            raise ValidationError('Salary cannot be negative.')
        return salary_min
    
    # ─── FORM-LEVEL VALIDATION ───
    # clean() runs after all field-level validation passes
    # Used for cross-field validation
    
    def clean(self):
        """Form-level validation — validates multiple fields together."""
        # super().clean() returns all cleaned_data collected so far
        cleaned_data = super().clean()
        
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        # Cross-field validation: max must be ≥ min
        if salary_min and salary_max:
            if salary_max < salary_min:
                raise ValidationError(
                    'Maximum salary must be greater than or equal to minimum salary.'
                )
        
        return cleaned_data


# ============================================================
# forms.Form — manual form, not tied to a model
# ============================================================

class ApplicationForm(forms.ModelForm):
    """
    ModelForm for job applications.
    Demonstrates: FileField, custom validators, BooleanField
    """
    
    # Extra field not in model — confirmation checkbox
    # BooleanField with required=True means it must be checked
    terms_accepted = forms.BooleanField(
        required=True,
        label='I confirm all information is accurate',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        error_messages={'required': 'You must confirm your information is accurate.'}
    )
    
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 7,
                'placeholder': 'Tell us why you are a great fit for this role...',
                'class': 'form-textarea',
            }),
        }
    
    # Override the resume field to add custom validators
    resume = forms.FileField(
        required=False,
        validators=[validate_pdf_or_doc, validate_file_size],
        widget=forms.FileInput(attrs={'class': 'form-file', 'accept': '.pdf,.doc,.docx'}),
        help_text='Optional. PDF or Word document, max 5MB.'
    )
    
    def clean_cover_letter(self):
        """Ensure cover letter has enough content."""
        letter = self.cleaned_data.get('cover_letter', '')
        word_count = len(letter.split())
        if word_count < 30:
            raise ValidationError(
                f'Cover letter is too short ({word_count} words). '
                'Please write at least 30 words.'
            )
        return letter


# ============================================================
# forms.Form — pure form (no model), for search
# ============================================================

class JobSearchForm(forms.Form):
    """
    Plain forms.Form — not tied to any model.
    Used for filtering the job list.
    """
    
    # CharField with optional widget override
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Job title, company, or keyword...',
            'class': 'form-input search-input',
        })
    )
    
    # ChoiceField — renders as <select>
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Any location...',
            'class': 'form-input',
        })
    )