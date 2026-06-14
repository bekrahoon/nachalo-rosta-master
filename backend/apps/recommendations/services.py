"""
AI-powered event recommendation service using OpenRouter
(OpenAI-compatible endpoint, free-tier models).
"""

import json
import logging

from django.conf import settings
from django.utils import timezone

from openai import OpenAI

from apps.events.models import Event, EventStatus
from .models import EventRecommendation

logger = logging.getLogger(__name__)

RECOMMENDATION_MODEL = 'openai/gpt-oss-120b:free'

RECOMMENDATION_TOOL = {
    'type': 'function',
    'function': {
        'name': 'submit_recommendations',
        'description': 'Сохранить список рекомендованных волонтёру мероприятий.',
        'parameters': {
            'type': 'object',
            'properties': {
                'recommendations': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'event_id': {'type': 'string'},
                            'match_score': {'type': 'number', 'minimum': 0, 'maximum': 100},
                            'reason': {'type': 'string'},
                        },
                        'required': ['event_id', 'match_score', 'reason'],
                    },
                },
            },
            'required': ['recommendations'],
        },
    },
}


def _get_client():
    api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENROUTER_API_KEY is not configured')
    return OpenAI(api_key=api_key, base_url=settings.OPENROUTER_API_BASE)


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
        "Ты — система рекомендаций волонтёрских мероприятий. "
        "На основе профиля волонтёра и списка доступных мероприятий выбери те, "
        "которые лучше всего соответствуют его интересам и навыкам.\n\n"
        f"Профиль волонтёра:\n{json.dumps(user_profile, ensure_ascii=False)}\n\n"
        f"Доступные мероприятия:\n{json.dumps(events_payload, ensure_ascii=False)}\n\n"
        "Вызови инструмент submit_recommendations со списком мероприятий, у которых "
        "match_score >= 40, отсортированных по убыванию match_score. Поле reason — "
        "короткое объяснение причины совпадения на русском языке."
    )


def generate_recommendations_for_user(user, limit=30):
    """
    Call the OpenRouter API to score unassigned events for a user and persist
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
        max_tokens=2048,
        temperature=0.3,
        tools=[RECOMMENDATION_TOOL],
        tool_choice={'type': 'function', 'function': {'name': 'submit_recommendations'}},
        messages=[{'role': 'user', 'content': prompt}],
    )

    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        logger.error('OpenRouter recommendation response did not contain a tool call')
        return []

    tool_input = json.loads(tool_calls[0].function.arguments)
    recommendations_data = tool_input.get('recommendations', [])

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
