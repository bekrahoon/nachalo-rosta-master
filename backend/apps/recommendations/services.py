"""
AI-powered event recommendation service using the OpenAI API.
"""

import json
import logging

from django.conf import settings
from django.utils import timezone

from openai import OpenAI

from apps.events.models import Event, EventStatus
from .models import EventRecommendation

logger = logging.getLogger(__name__)

RECOMMENDATION_MODEL = 'gpt-4o-mini'


def _get_client():
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured')
    return OpenAI(api_key=api_key)


def _get_unassigned_events(user, limit=30):
    """
    Events the user hasn't joined yet, that are upcoming and still open.
    """
    return (
        Event.objects.filter(
            status__in=[EventStatus.UPCOMING, EventStatus.ONGOING],
            start_date__gte=timezone.now(),
        )
        .exclude(eventvolunteer__volunteer=user)
        .order_by('start_date')[:limit]
    )


def _build_event_payload(events):
    return [
        {
            'id': str(event.id),
            'title': event.title,
            'description': (event.description or '')[:300],
            'category': event.get_category_display(),
            'location': event.location,
            'required_skills': event.required_skills,
            'volunteer_hours': event.volunteer_hours,
            'start_date': event.start_date.isoformat(),
        }
        for event in events
    ]


def _build_user_profile(user):
    return {
        'interests': user.interests or [],
        'skills': user.skills or [],
        'city': user.city,
        'bio': (user.bio or '')[:300],
    }


def _build_prompt(user_profile, events_payload):
    return (
        "You are a volunteering recommendation engine. "
        "Given a volunteer's profile and a list of available volunteering events, "
        "select the events that best match the volunteer's interests and skills.\n\n"
        f"Volunteer profile:\n{json.dumps(user_profile, ensure_ascii=False)}\n\n"
        f"Available events:\n{json.dumps(events_payload, ensure_ascii=False)}\n\n"
        "Return ONLY a JSON object with a single key \"recommendations\", whose value is "
        "an array of objects with keys \"event_id\" (string), \"match_score\" (number 0-100), "
        "and \"reason\" (short string explaining the match in Russian). "
        "Only include events with match_score >= 40. Order by match_score descending."
    )


def generate_recommendations_for_user(user, limit=30):
    """
    Call the OpenAI API to score unassigned events for a user and persist
    the results as EventRecommendation rows.

    Returns the list of EventRecommendation instances created/updated.
    """
    events = list(_get_unassigned_events(user, limit=limit))
    if not events:
        return []

    events_by_id = {str(event.id): event for event in events}

    client = _get_client()
    prompt = _build_prompt(_build_user_profile(user), _build_event_payload(events))

    response = client.chat.completions.create(
        model=RECOMMENDATION_MODEL,
        messages=[
            {'role': 'system', 'content': 'You respond only with valid JSON.'},
            {'role': 'user', 'content': prompt},
        ],
        response_format={'type': 'json_object'},
        temperature=0.3,
    )

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error(f'Failed to parse OpenAI recommendation response: {exc}')
        return []

    recommendations_data = data.get('recommendations', [])

    results = []
    for item in recommendations_data:
        event_id = str(item.get('event_id', ''))
        event = events_by_id.get(event_id)
        if not event:
            continue

        try:
            match_score = float(item.get('match_score', 0))
        except (TypeError, ValueError):
            continue
        match_score = max(0.0, min(100.0, match_score))

        recommendation, _created = EventRecommendation.objects.update_or_create(
            user=user,
            event=event,
            defaults={
                'match_score': match_score,
                'reason': str(item.get('reason', ''))[:1000],
            },
        )
        results.append(recommendation)

    logger.info(f'Generated {len(results)} recommendations for {user.email}')
    return results
