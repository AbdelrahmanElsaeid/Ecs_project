
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import LoginHistory, Invitation

@shared_task
def expire_login_history():
    LoginHistory.objects.filter(
        timestamp__lt=timezone.now() - timedelta(days=365 * 5),
    ).delete()

@shared_task
def expire_invitations():
    Invitation.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=14),
        is_used=False
    ).update(is_used=True)

