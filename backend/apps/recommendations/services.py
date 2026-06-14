"""
AI-powered recommendation service for aggregator listings using OpenRouter
(OpenAI-compatible endpoint, free-tier models).
"""

import json
import logging

from django.conf import settings

from openai import OpenAI

from apps.aggregator.models import Listing, ListingStatus
from .models import EventRecommendation

logger = logging.getLogger(__name__)

RECOMMENDATION_MODEL = 'openai/gpt-oss-120b:free'

RECOMMENDATION_TOOL = {
    'type': 'function',
    'function': {
        'name': 'submit_recommendations',
        'description': 'Сохранить список рекомендованных пользователю объявлений (волонтёрство, гранты, мероприятия и т.д.).',
        'parameters': {
            'type': 'object',
            'properties': {
                'recommendations': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'listing_id': {'type': 'string'},
                            'match_score': {'type': 'number', 'minimum': 0, 'maximum': 100},
                            'reason': {'type': 'string'},
                        },
                        'required': ['listing_id', 'match_score', 'reason'],
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


def _get_candidate_listings(user, limit=40):
    """
    Published aggregator listings not yet recommended to the user.
    """
    return (
        Listing.objects.filter(status=ListingStatus.PUBLISHED)
        .exclude(recommendations__user=user)
        .order_by('-created_at')[:limit]
    )


def _build_listing_payload(listings):
    return [
        {
            'id': str(listing.id),
            'title': listing.title,
            'description': (listing.description or '')[:300],
            'listing_type': listing.get_listing_type_display(),
            'organization': listing.organization_name,
            'region': listing.region,
            'is_online': listing.is_online,
            'tags': [tag.name for tag in listing.tags.all()],
        }
        for listing in listings
    ]


def _build_user_profile(user):
    return {
        'interests': user.interests or [],
        'skills': user.skills or [],
        'city': user.city,
        'bio': (user.bio or '')[:300],
    }


def _build_prompt(user_profile, listings_payload):
    return (
        "Ты — система рекомендаций для платформы-агрегатора волонтёрских программ, "
        "грантов, стажировок, хакатонов и образовательных возможностей для студентов. "
        "На основе профиля пользователя и списка доступных объявлений выбери те, "
        "которые лучше всего соответствуют его интересам и навыкам.\n\n"
        f"Профиль пользователя:\n{json.dumps(user_profile, ensure_ascii=False)}\n\n"
        f"Доступные объявления:\n{json.dumps(listings_payload, ensure_ascii=False)}\n\n"
        "Вызови инструмент submit_recommendations со списком объявлений, у которых "
        "match_score >= 40, отсортированных по убыванию match_score. Поле reason — "
        "короткое объяснение причины совпадения на русском языке."
    )


def generate_recommendations_for_user(user, limit=40):
    """
    Call the OpenRouter API to score published listings for a user and persist
    the results as EventRecommendation rows.

    Returns the list of EventRecommendation instances created/updated.
    """
    listings = list(_get_candidate_listings(user, limit=limit))
    if not listings:
        return []

    listings_by_id = {str(listing.id): listing for listing in listings}

    client = _get_client()
    prompt = _build_prompt(_build_user_profile(user), _build_listing_payload(listings))

    recommendations_data = []
    for attempt in range(2):
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
            continue

        try:
            tool_input = json.loads(tool_calls[0].function.arguments)
        except json.JSONDecodeError:
            logger.warning('OpenRouter returned invalid JSON for recommendations (attempt %d)', attempt + 1)
            continue

        recommendations_data = tool_input.get('recommendations', [])
        break

    results = []
    for item in recommendations_data:
        listing_id = str(item.get('listing_id', ''))
        listing = listings_by_id.get(listing_id)
        if not listing:
            continue

        try:
            match_score = float(item.get('match_score', 0))
        except (TypeError, ValueError):
            continue
        match_score = max(0.0, min(100.0, match_score))

        recommendation, _created = EventRecommendation.objects.update_or_create(
            user=user,
            listing=listing,
            defaults={
                'match_score': match_score,
                'reason': str(item.get('reason', ''))[:1000],
            },
        )
        results.append(recommendation)

    logger.info(f'Generated {len(results)} recommendations for {user.email}')
    return results
