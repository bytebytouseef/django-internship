from django.db import models
from django.conf import settings
from apps.interns.models import Intern

class Assignment(models.Model):
    """
    Assignment model for tasks assigned to interns.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    
    assigned_to = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.assigned_to.full_name}"


class AssignmentSubmission(models.Model):
    """
    Submission model for assignment work submitted by interns.
    """
    SUBMISSION_STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name='submissions')
    
    submission_url = models.URLField(blank=True, null=True)
    submission_text = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='submitted')
    reviewer_feedback = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission for {self.assignment.title} by {self.submitted_by.full_name}"
