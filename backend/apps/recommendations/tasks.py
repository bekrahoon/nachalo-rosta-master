"""
Celery tasks for AI-powered event recommendations.
"""

from celery import shared_task
from django.contrib.auth import get_user_model
import logging

from .services import generate_recommendations_for_user

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_recommendations(self, user_id):
    """
    Generate AI event recommendations for a single user.
    """
    try:
        user = User.objects.get(id=user_id)
        recommendations = generate_recommendations_for_user(user)
        return f'Generated {len(recommendations)} recommendations for {user.email}'
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
        return 'User not found'
    except Exception as exc:
        logger.error(f'Error generating recommendations for user {user_id}: {exc}')
        raise self.retry(exc=exc)


@shared_task
def generate_recommendations_for_all_users():
    """
    Fan out recommendation generation for all active users.
    Runs daily via celery beat.
    """
    user_ids = User.objects.filter(is_active=True).values_list('id', flat=True)

    queued = 0
    for user_id in user_ids:
        generate_recommendations.delay(str(user_id))
        queued += 1

    logger.info(f'Queued recommendation generation for {queued} users')
    return f'Queued {queued} users'
