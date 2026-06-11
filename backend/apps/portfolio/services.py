"""
Aggregation helpers for building a volunteer's portfolio.
"""

from django.db.models import Sum

from apps.events.models import EventVolunteer
from apps.achievements.services import get_or_create_stats


def build_portfolio_context(user):
    """
    Aggregate a user's completed events, total volunteered hours,
    and unlocked achievements into a single context dict, used both
    by the JSON summary endpoint and the PDF export template.
    """
    completed_participations = (
        EventVolunteer.objects.filter(volunteer=user, status='completed')
        .select_related('event')
        .order_by('-completed_at')
    )

    total_hours = completed_participations.aggregate(
        total=Sum('hours_completed')
    )['total'] or 0

    stats = get_or_create_stats(user)
    badges = user.badges.select_related('badge').order_by('-unlocked_at')

    return {
        'user': user,
        'stats': stats,
        'total_hours': total_hours,
        'completed_events': [p.event for p in completed_participations],
        'participations': completed_participations,
        'badges': [ub.badge for ub in badges],
    }
