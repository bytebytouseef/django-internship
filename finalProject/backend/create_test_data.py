"""
Create test data for the application.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.interns.models import Intern
from apps.assignments.models import Assignment

# Create a regular intern user
intern_user = User.objects.create_user(
    email='intern@example.com',
    username='intern1',
    password='intern123',
    first_name='John',
    last_name='Doe'
)

# Create intern profile
intern = Intern.objects.create(
    user=intern_user,
    full_name='John Doe',
    email='intern@example.com',
    department='Engineering',
    phone='555-1234',
    date_of_birth='2000-01-15',
    resume_url='https://example.com/resume.pdf',
    skills='Python, Django, JavaScript',
    start_date=timezone.now().date(),
    end_date=timezone.now().date() + timedelta(days=90),
    assigned_mentor=User.objects.get(username='admin')
)

# Create some assignments
admin = User.objects.get(username='admin')
Assignment.objects.create(
    title='Build Login Feature',
    description='Implement user authentication with JWT tokens',
    due_date=timezone.now() + timedelta(days=7),
    assigned_to=intern,
    created_by=admin,
    status='pending'
)

Assignment.objects.create(
    title='Create REST API',
    description='Build REST API endpoints for intern management',
    due_date=timezone.now() + timedelta(days=14),
    assigned_to=intern,
    created_by=admin,
    status='pending'
)

print("Test data created successfully!")
print("Admin: admin@localhost.com / admin123")
print("Intern: intern@example.com / intern123")
