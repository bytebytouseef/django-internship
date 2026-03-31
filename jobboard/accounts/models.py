from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser.
    MUST be defined before running any migrations.
    AbstractUser gives us: username, email, password,
    first_name, last_name, is_staff, is_active, date_joined
    We add company-specific fields on top.
    """
    
    # Distinguishes company accounts from applicant accounts
    is_company = models.BooleanField(default=False)
    
    # Extra profile fields
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        if self.is_company and self.company_name:
            return self.company_name
        return self.username
    
    def get_display_name(self):
        return self.company_name if self.is_company else self.get_full_name() or self.username