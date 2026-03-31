from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Application, Job

User = get_user_model()


@receiver(post_save, sender=Application)
def application_created_handler(sender, instance, created, **kwargs):
    """
    post_save fires AFTER an object is saved.
    'created=True' means it's a new record, not an update.
    
    Practical use: send email notification, create activity log, etc.
    """
    if created:
        print(f"[SIGNAL] New application: {instance.applicant.username} "
              f"applied to '{instance.job.title}'")
        # In production: send_mail(...) or trigger a Celery task


@receiver(post_save, sender=User)
def setup_company_profile(sender, instance, created, **kwargs):
    """
    When a new company user is created, auto-fill company_name
    from username if it's empty.
    """
    if created and instance.is_company and not instance.company_name:
        User.objects.filter(pk=instance.pk).update(
            company_name=instance.username.replace('_', ' ').title()
        )


@receiver(pre_delete, sender=Job)
def job_pre_delete_handler(sender, instance, **kwargs):
    """
    pre_delete fires BEFORE an object is deleted.
    Use it to clean up related files, log the action, etc.
    """
    print(f"[SIGNAL] Job '{instance.title}' by '{instance.posted_by}' "
          f"is being deleted. Applications: {instance.applications.count()}")