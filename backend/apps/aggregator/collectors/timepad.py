"""
Коллектор для официального REST API Timepad (https://dev.timepad.ru/).

Требует TIMEPAD_API_TOKEN (settings/.env). Если токен не задан, источник
просто пропускается — это позволяет держать его в SOURCES_SEED без ошибок,
пока токен не получен.
"""

import json
import logging
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from django.conf import settings

from .base import BaseCollector, CollectedItem, register_collector

logger = logging.getLogger(__name__)

EVENTS_URL = 'https://api.timepad.ru/v1/events'
DEFAULT_FIELDS = 'description_html,description_short,location,organization,categories,poster_image'


@register_collector('timepad_api')
class TimepadCollector(BaseCollector):
    """Запрашивает свежие события Timepad и нормализует их в CollectedItem."""

    def fetch(self, source) -> list[CollectedItem]:
        token = getattr(settings, 'TIMEPAD_API_TOKEN', '')
        if not token:
            logger.info('TIMEPAD_API_TOKEN не задан — источник "%s" пропущен', source.name)
            return []

        params = {
            'limit': 50,
            'sort': '-publication_date',
            'fields': DEFAULT_FIELDS,
        }
        params.update(source.config.get('query_params', {}))

        response = httpx.get(
            EVENTS_URL,
            params=params,
            headers={'Authorization': f'Bearer {token}'},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for event in data.get('values', []):
            event_id = event.get('id')
            if event_id is None:
                continue

            description_html = event.get('description_html') or ''
            description = BeautifulSoup(description_html, 'html.parser').get_text('\n', strip=True)
            if not description:
                description = event.get('description_short', '')

            text_parts = [event.get('name', '')]

            organization = (event.get('organization') or {}).get('name')
            if organization:
                text_parts.append(f'Организатор: {organization}')

            city = (event.get('location') or {}).get('city')
            if city:
                text_parts.append(f'Город: {city}')

            if description:
                text_parts.append(description)

            published_at = None
            starts_at = event.get('starts_at')
            if starts_at:
                try:
                    published_at = datetime.fromisoformat(starts_at)
                except ValueError:
                    pass

            poster = event.get('poster_image') or {}
            media_urls = []
            poster_url = poster.get('default_url') or poster.get('url')
            if poster_url:
                media_urls.append(poster_url)

            items.append(CollectedItem(
                external_id=str(event_id),
                raw_text='\n'.join(filter(None, text_parts)),
                source_url=event.get('url', ''),
                raw_payload=json.dumps(event, ensure_ascii=False),
                media_urls=media_urls,
                published_at=published_at,
            ))

        return items
