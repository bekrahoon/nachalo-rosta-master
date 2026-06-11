"""
Signal handlers that trigger achievement/stat updates.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.events.models import EventVolunteer
from .services import update_stats_on_event_completion


@receiver(pre_save, sender=EventVolunteer)
def capture_previous_status(sender, instance, **kwargs):
    """Stash the previous status on the instance so post_save can detect a transition."""
    if instance.pk:
        previous = EventVolunteer.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
        instance._previous_status = previous
    else:
        instance._previous_status = None


@receiver(post_save, sender=EventVolunteer)
def handle_event_volunteer_completed(sender, instance, created, **kwargs):
    """
    When a volunteer's participation transitions to 'completed', update their
    stats (hours/events/points) and check for newly unlocked badges.
    """
    if instance.status != 'completed':
        return

    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == 'completed':
        # Already processed - avoid double-counting on subsequent saves
        return

    update_stats_on_event_completion(instance.volunteer, instance.hours_completed)
