"""
Django signals for accounts app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Actions before saving user.
    """
    if instance.pk:
        # Check if email is being changed
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.email != instance.email:
                # Email was changed, require verification
                instance.email_verified = False
                logger.info(f'Email changed for user {instance.id}, requiring re-verification')
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Actions after saving user.
    """
    if created:
        logger.info(f'New user created: {instance.email}')
        # Additional setup could go here
    else:
        logger.info(f'User updated: {instance.email}')
