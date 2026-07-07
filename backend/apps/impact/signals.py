"""
Signal handlers that record social impact data.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.events.models import EventVolunteer
from .models import ImpactRecord


@receiver(pre_save, sender=EventVolunteer, dispatch_uid='impact_capture_previous_status')
def capture_previous_status(sender, instance, **kwargs):
    """Stash the previous status so post_save can detect a transition to 'completed'."""
    if instance.pk:
        previous = EventVolunteer.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
        instance._impact_previous_status = previous
    else:
        instance._impact_previous_status = None


@receiver(post_save, sender=EventVolunteer, dispatch_uid='impact_record_on_completion')
def record_impact_on_completion(sender, instance, created, **kwargs):
    """
    When a volunteer's participation transitions to 'completed', record the
    contributed hours as an ImpactRecord for analytics/reporting.
    """
    if instance.status != 'completed':
        return

    if getattr(instance, '_impact_previous_status', None) == 'completed':
        return

    ImpactRecord.objects.get_or_create(
        user=instance.volunteer,
        event=instance.event,
        defaults={'hours_contributed': instance.hours_completed},
    )
