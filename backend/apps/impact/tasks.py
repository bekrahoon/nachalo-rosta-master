"""
Celery tasks for the impact app.
"""

from celery import shared_task
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import logging

from apps.achievements.models import Stats
from .models import ImpactRecord

logger = logging.getLogger(__name__)


@shared_task
def calculate_impact_statistics():
    """
    Recalculate each user's "best month" volunteering stats from their
    impact records. Runs daily at midnight via celery beat.
    """
    updated = 0

    for stats in Stats.objects.select_related('user'):
        best = (
            ImpactRecord.objects.filter(user=stats.user)
            .annotate(month=TruncMonth('recorded_at'))
            .values('month')
            .annotate(hours=Sum('hours_contributed'))
            .order_by('-hours')
            .first()
        )
        if best and best['hours'] and best['hours'] > stats.best_month_hours:
            stats.best_month_hours = best['hours']
            stats.best_month = best['month'].strftime('%Y-%m')
            stats.save(update_fields=['best_month_hours', 'best_month', 'updated_at'])
            updated += 1

    logger.info(f'Updated best-month stats for {updated} users')
    return f'Updated {updated} users'
