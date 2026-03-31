from django.db import models
from django.conf import settings
from django.core.validators import URLValidator

class Intern(models.Model):
    """
    Intern profile model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intern_profile')
    
    # Basic Info
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    
    # Contact & Personal
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Resume & Skills
    resume_url = models.URLField(blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    
    # Internship Dates & Mentor
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_interns')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"
