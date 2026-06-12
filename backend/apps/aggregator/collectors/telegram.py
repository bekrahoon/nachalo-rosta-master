"""
Коллектор для публичного веб-просмотра Telegram-каналов (https://t.me/s/<channel>).

Не требует авторизации/токена — подходит для MVP. Возвращает последние посты
с превью-страницы канала (как правило, ~20 последних сообщений).
"""

import logging
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from .base import BaseCollector, CollectedItem, register_collector

logger = logging.getLogger(__name__)

PREVIEW_URL = 'https://t.me/s/{channel}'
USER_AGENT = 'Mozilla/5.0 (compatible; NachaloRostaBot/1.0)'


@register_collector('telegram_web_preview')
class TelegramWebCollector(BaseCollector):
    """Парсит HTML-превью канала и извлекает текстовые посты."""

    def fetch(self, source) -> list[CollectedItem]:
        url = PREVIEW_URL.format(channel=source.identifier)
        response = httpx.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        items = []

        for message in soup.select('div.tgme_widget_message[data-post]'):
            text_el = message.select_one('div.tgme_widget_message_text')
            text = text_el.get_text('\n', strip=True) if text_el else ''
            if not text:
                continue

            post_path = message['data-post']
            external_id = post_path.split('/')[-1]

            published_at = None
            time_el = message.select_one('time[datetime]')
            if time_el:
                try:
                    published_at = datetime.fromisoformat(time_el['datetime'])
                except ValueError:
                    pass

            media_urls = []
            for photo in message.select('a.tgme_widget_message_photo_wrap'):
                match = re.search(r"url\(['\"]?(.+?)['\"]?\)", photo.get('style', ''))
                if match:
                    media_urls.append(match.group(1))

            items.append(CollectedItem(
                external_id=external_id,
                raw_text=text,
                source_url=f'https://t.me/{post_path}',
                raw_payload=str(message),
                media_urls=media_urls,
                published_at=published_at,
            ))

        return items
