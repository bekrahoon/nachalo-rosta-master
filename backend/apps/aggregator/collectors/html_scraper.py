"""
Универсальный HTML-скрейпер для сайтов без API.

config источника (все необязательны):
    article_selector:      CSS-селектор карточки/статьи (default: 'article')
    title_selector:        CSS-селектор заголовка внутри карточки (default: 'h2 a, h3 a, h2, h3')
    description_selector:  CSS-селектор описания (default: 'p')
    link_selector:         CSS-селектор ссылки (default: 'a')
"""

import hashlib
import logging
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .base import BaseCollector, CollectedItem, register_collector

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (compatible; NachaloRostaBot/1.0)'


@register_collector('html_scrape')
class HtmlScrapeCollector(BaseCollector):

    def fetch(self, source) -> list[CollectedItem]:
        url = source.url or source.identifier
        config = source.config or {}

        article_sel = config.get('article_selector', 'article')
        title_sel = config.get('title_selector', 'h2 a, h3 a, h2, h3')
        desc_sel = config.get('description_selector', 'p')
        link_sel = config.get('link_selector', 'a')

        response = httpx.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        items = []

        for card in soup.select(article_sel):
            title_el = card.select_one(title_sel)
            title = title_el.get_text(strip=True) if title_el else ''

            desc_el = card.select_one(desc_sel)
            description = desc_el.get_text('\n', strip=True) if desc_el else ''

            raw_text = '\n'.join(filter(None, [title, description]))
            if not raw_text:
                continue

            link_el = title_el if title_el and title_el.name == 'a' else card.select_one(link_sel)
            link = ''
            if link_el and link_el.get('href'):
                link = urljoin(url, link_el['href'])

            external_id = hashlib.md5((link or raw_text).encode()).hexdigest()[:16]

            media_urls = []
            img = card.select_one('img')
            if img and img.get('src'):
                media_urls.append(urljoin(url, img['src']))

            items.append(CollectedItem(
                external_id=external_id,
                raw_text=raw_text,
                source_url=link,
                raw_payload=str(card),
                media_urls=media_urls,
            ))

        return items
