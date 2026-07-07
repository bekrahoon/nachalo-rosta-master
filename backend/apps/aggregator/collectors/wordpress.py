"""
Универсальный коллектор для WordPress REST API (/wp-json/wp/v2/posts/).

Подходит для любого сайта на WordPress с включённым REST API (включён по
умолчанию начиная с WP 4.7) — не требует токена и не зависит от RSS-фидов,
которые на многих сайтах отключены настройками безопасности.

config источника:
    api_url: URL эндпоинта posts, например
        'https://example.com/wp-json/wp/v2/posts'
    params: доп. query-параметры запроса (например {'categories': 16})
"""

import logging
from datetime import datetime, timezone as dt_timezone

import httpx
from bs4 import BeautifulSoup

from .base import BaseCollector, CollectedItem, register_collector

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (compatible; NachaloRostaBot/1.0)'
DEFAULT_PARAMS = {'per_page': 20, 'orderby': 'date', 'order': 'desc', '_embed': 1}


@register_collector('wordpress_api')
class WordPressApiCollector(BaseCollector):
    """Запрашивает последние записи через WordPress REST API."""

    def fetch(self, source) -> list[CollectedItem]:
        api_url = source.config.get('api_url') or source.url or source.identifier

        params = dict(DEFAULT_PARAMS)
        params.update(source.config.get('params', {}))

        response = httpx.get(
            api_url,
            params=params,
            headers={'User-Agent': USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()

        items = []
        for post in response.json():
            post_id = post.get('id')
            if post_id is None:
                continue

            title = BeautifulSoup((post.get('title') or {}).get('rendered', ''), 'html.parser').get_text(strip=True)

            content_html = (post.get('content') or {}).get('rendered', '')
            body_text = BeautifulSoup(content_html, 'html.parser').get_text('\n', strip=True)

            raw_text = '\n'.join(part for part in (title, body_text) if part)
            if not raw_text:
                continue

            published_at = None
            date_gmt = post.get('date_gmt')
            if date_gmt:
                try:
                    published_at = datetime.fromisoformat(date_gmt).replace(tzinfo=dt_timezone.utc)
                except ValueError:
                    pass

            media_urls = []
            featured = (post.get('_embedded') or {}).get('wp:featuredmedia') or []
            if featured and featured[0].get('source_url'):
                media_urls.append(featured[0]['source_url'])
            else:
                img = BeautifulSoup(content_html, 'html.parser').find('img')
                if img and img.get('src'):
                    media_urls.append(img['src'])

            items.append(CollectedItem(
                external_id=str(post_id),
                raw_text=raw_text,
                source_url=post.get('link', ''),
                raw_payload=content_html,
                media_urls=media_urls,
                published_at=published_at,
            ))

        return items
