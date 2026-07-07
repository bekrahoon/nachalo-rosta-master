"""
Celery tasks for accounts app.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id):
    """
    Send password reset link to user.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prepare email context
        reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={user.password_reset_token}"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'token': user.password_reset_token,
            'site_name': 'Nachalo Rosta',
        }
        
        # Render HTML email
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
        
        # Send email
        send_mail(
            subject=_('Password reset request - Nachalo Rosta'),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Password reset email sent to {user.email}')
        return f'Password reset email sent to {user.email}'
    
    except User.DoesNotExist:
        logger.error(f'User with id {user_id} not found')
        return f'User not found'
    
    except Exception as exc:
        logger.error(f'Error sending password reset email: {str(exc)}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Send welcome email to newly verified user.
    """
    try:
        user = User.objects.get(id=user_id, email_verified=True)
        
        context = {
            'user': user,
            'site_name': 'Nachalo Rosta',
        }
        
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)
        
        send_mail(
            subject=_('Welcome to Nachalo Rosta!'),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Welcome email sent to {user.email}')
        return f'Welcome email sent to {user.email}'
    
    except Exception as exc:
        logger.error(f'Error sending welcome email: {str(exc)}')
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_tokens():
    """
    Clean up expired password reset tokens.
    Runs daily at 2 AM.
    """
    now = timezone.now()

    # Clean expired password reset tokens (1 hour old)
    password_reset_expiration = now - timedelta(hours=1)
    expired_reset = User.objects.filter(
        password_reset_token_created__lt=password_reset_expiration,
        password_reset_token__isnull=False
    )
    count = expired_reset.update(
        password_reset_token=None,
        password_reset_token_created=None
    )
    logger.info(f'Cleaned {count} expired password reset tokens')
    
    return 'Cleanup completed'


@shared_task
def cleanup_old_sessions():
    """
    Clean up old user sessions.
    Runs daily.
    """
    from .models import UserSession
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = UserSession.objects.filter(last_activity__lt=cutoff_date).delete()[0]
    
    logger.info(f'Deleted {deleted_count} old user sessions')
    return f'Deleted {deleted_count} old sessions'


@shared_task
def send_notification_email(user_id, subject, template_name, context=None):
    """
    Generic task to send notification emails.
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.receive_emails:
            logger.info(f'User {user.email} has notifications disabled')
            return f'User has notifications disabled'
        
        if context is None:
            context = {}
        
        context['user'] = user
        context['site_name'] = 'Nachalo Rosta'
        
        html_message = render_to_string(f'emails/{template_name}.html', context)
        plain_message = render_to_string(f'emails/{template_name}.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Notification email sent to {user.email}')
        return f'Notification sent to {user.email}'
    
    except User.DoesNotExist:
        logger.error(f'User with id {user_id} not found')
        return f'User not found'
    
    except Exception as exc:
        logger.error(f'Error sending notification: {str(exc)}')
        return f'Error: {str(exc)}'
