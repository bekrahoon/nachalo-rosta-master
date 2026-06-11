"""
Celery tasks for the achievements app.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import UserBadge

logger = logging.getLogger(__name__)


@shared_task
def send_pending_notifications():
    """
    Notify users by email about badges they unlocked recently
    that they haven't been notified about yet.
    Runs every 6 hours via celery beat.
    """
    from apps.accounts.tasks import send_notification_email

    cutoff = timezone.now() - timedelta(hours=6)
    recent_badges = UserBadge.objects.filter(unlocked_at__gte=cutoff).select_related('user', 'badge')

    sent = 0
    for user_badge in recent_badges:
        send_notification_email.delay(
            user_id=str(user_badge.user.id),
            subject='Новое достижение разблокировано!',
            template_name='achievement',
            context={'badge': {
                'name': user_badge.badge.name,
                'description': user_badge.badge.description,
                'icon': user_badge.badge.icon,
            }},
        )
        sent += 1

    logger.info(f'Queued {sent} achievement notification emails')
    return f'Queued {sent} notifications'
