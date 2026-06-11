"""
Celery tasks for the events app.
"""

from celery import shared_task
from django.utils import timezone
import logging

from .models import Event, EventStatus

logger = logging.getLogger(__name__)


@shared_task
def check_event_deadlines():
    """
    Periodically update event statuses based on their start/end dates:
    - upcoming events whose start_date has passed -> ongoing
    - ongoing events whose end_date has passed -> completed
    Runs hourly via celery beat.
    """
    now = timezone.now()

    started = Event.objects.filter(
        status=EventStatus.UPCOMING,
        start_date__lte=now,
    ).update(status=EventStatus.ONGOING)

    finished = Event.objects.filter(
        status=EventStatus.ONGOING,
        end_date__lte=now,
    ).update(status=EventStatus.COMPLETED)

    logger.info(f'Event statuses updated: {started} started, {finished} completed')
    return f'{started} events started, {finished} events completed'
