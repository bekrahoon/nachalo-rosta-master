"""
Service layer for achievements: stats tracking and badge awarding.
"""

import logging

from .models import Badge, BadgeCriteriaType, Level, Stats, UserBadge

logger = logging.getLogger(__name__)


def get_or_create_stats(user):
    """Return the Stats object for a user, creating it if needed."""
    stats, _created = Stats.objects.get_or_create(user=user)
    return stats


def update_stats_on_event_completion(user, hours_completed):
    """
    Increment a user's volunteering stats after an event is marked completed,
    then check whether any new badges should be awarded.
    Returns the updated Stats instance and a list of newly awarded Badge instances.
    """
    stats = get_or_create_stats(user)

    stats.total_hours += hours_completed or 0
    stats.total_events += 1
    stats.total_points += 10

    _update_best_month(stats)
    _update_level(stats)

    stats.save()

    new_badges = check_and_award_badges(user, stats)

    return stats, new_badges


def update_stats_on_team_join(user):
    """Increment a user's team count and re-check badges."""
    stats = get_or_create_stats(user)
    stats.total_teams += 1
    stats.save(update_fields=['total_teams', 'updated_at'])

    new_badges = check_and_award_badges(user, stats)
    return stats, new_badges


def _update_best_month(stats):
    """Track the month with the most volunteering hours."""
    from django.utils import timezone

    current_month = timezone.now().strftime('%Y-%m')
    if current_month == stats.best_month:
        # Already the best month being tracked - leave best_month_hours as-is,
        # it gets recalculated by the impact analytics endpoint.
        return
    if not stats.best_month:
        stats.best_month = current_month


def _update_level(stats):
    """Assign the highest Level whose min_points threshold the user has reached."""
    level = (
        Level.objects.filter(min_points__lte=stats.total_points)
        .order_by('-min_points')
        .first()
    )
    if level:
        stats.level = level


def check_and_award_badges(user, stats=None):
    """
    Check all badges against the user's current stats and award any
    that have been newly earned. Returns a list of newly-awarded Badge instances.
    """
    if stats is None:
        stats = get_or_create_stats(user)

    already_earned_ids = set(
        UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    )

    progress_by_criteria = {
        BadgeCriteriaType.EVENTS_COMPLETED: stats.total_events,
        BadgeCriteriaType.HOURS_COMPLETED: stats.total_hours,
        BadgeCriteriaType.TEAMS_JOINED: stats.total_teams,
    }

    newly_awarded = []

    candidate_badges = Badge.objects.exclude(id__in=already_earned_ids)
    for badge in candidate_badges:
        progress = progress_by_criteria.get(badge.criteria_type)
        if progress is None:
            continue
        if progress >= badge.criteria_value:
            UserBadge.objects.create(user=user, badge=badge)
            newly_awarded.append(badge)
            logger.info(f'Awarded badge "{badge.name}" to {user.email}')

    if newly_awarded:
        stats.total_points += sum(b.points for b in newly_awarded)
        _update_level(stats)
        stats.save(update_fields=['total_points', 'level', 'updated_at'])

    return newly_awarded
