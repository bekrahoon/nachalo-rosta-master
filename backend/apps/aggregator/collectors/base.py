"""
Базовые классы и реестр коллекторов источников.

Каждый коллектор регистрируется под именем fetch_method, которое указывается
в поле Source.config (например, {'fetch_method': 'telegram_web_preview'}).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CollectedItem:
    """Один найденный пост/событие, нормализованный для сохранения в RawItem."""

    external_id: str
    raw_text: str
    source_url: str = ''
    raw_payload: str = ''
    media_urls: list[str] = field(default_factory=list)
    published_at: Optional[datetime] = None


class BaseCollector:
    """Коллектор источника: получает список новых элементов."""

    def fetch(self, source) -> list[CollectedItem]:
        raise NotImplementedError


_REGISTRY: dict[str, type[BaseCollector]] = {}


def register_collector(fetch_method: str):
    def decorator(cls):
        _REGISTRY[fetch_method] = cls
        return cls

    return decorator


def get_collector(source) -> Optional[BaseCollector]:
    fetch_method = (source.config or {}).get('fetch_method')
    collector_cls = _REGISTRY.get(fetch_method)
    return collector_cls() if collector_cls else None
