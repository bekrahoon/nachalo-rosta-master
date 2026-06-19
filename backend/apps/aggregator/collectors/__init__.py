"""
Импорт подмодулей регистрирует доступные коллекторы (см. base.register_collector).
"""

from . import html_scraper, rss, telegram, timepad, wordpress  # noqa: F401
from .base import CollectedItem, get_collector

__all__ = ['CollectedItem', 'get_collector']
