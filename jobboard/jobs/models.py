from django.db import models
from django.conf import settings

# get_user_model() — preferred over importing User directly
# It returns whatever AUTH_USER_MODEL is set to
from django.contrib.auth import get_user_model

User = get_user_model()


def company_logo_path(instance, filename):
    """Dynamic upload path: media/logos/company_<id>/<filename>"""
    return f'logos/company_{instance.posted_by.id}/{filename}'


def resume_upload_path(instance, filename):
    """Dynamic upload path: media/resumes/job_<id>/<filename>"""
    return f'resumes/job_{instance.job.id}/{filename}'


class Job(models.Model):
    
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
        ('lead', 'Lead / Manager'),
    ]

    # ForeignKey — many jobs → one company user
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        limit_choices_to={'is_company': True}
    )
    
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    
    # ImageField requires Pillow — stores in MEDIA_ROOT
    company_logo = models.ImageField(
        upload_to=company_logo_path,
        blank=True,
        null=True
    )
    
    description = models.TextField()
    requirements = models.TextField()
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default='full_time'
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='mid'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} at {self.company_name}'
    
    def get_salary_display_text(self):
        if self.salary_min and self.salary_max:
            return f'${self.salary_min:,} – ${self.salary_max:,}'
        elif self.salary_min:
            return f'From ${self.salary_min:,}'
        return 'Negotiable'


class Application(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    # select_related() works on ForeignKey — fetches in a single JOIN query
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    cover_letter = models.TextField()
    
    # FileField — for resume PDFs; ImageField — for images (adds validation)
    resume = models.FileField(
        upload_to=resume_upload_path,
        blank=True,
        null=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        # Prevent duplicate applications
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f'{self.applicant.username} → {self.job.title}'