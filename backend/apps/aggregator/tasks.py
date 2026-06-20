"""
Celery-задачи сбора объявлений (Этап 1): обход активных источников и
сохранение найденных постов/событий в RawItem.
"""

import hashlib
import logging
import re
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.text import slugify

from . import classifier
from .collectors import get_collector
from .models import (
    Listing,
    ListingStatus,
    ListingType,
    RawItem,
    RawItemStatus,
    Source,
    SourceTrustLevel,
    Tag,
)

logger = logging.getLogger(__name__)

CLASSIFY_BATCH_SIZE = 20


def _content_hash(text: str) -> str:
    """Хэш нормализованного текста — для обнаружения дублей между источниками."""
    normalized = re.sub(r'\s+', ' ', text.strip().lower())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def _clamp(value, lo, hi):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, value))


def _parse_ai_date(value):
    """Парсит дату/дату-время от AI (ISO 8601) в aware datetime, либо None."""
    if not isinstance(value, str) or not value.strip():
        return None

    parsed = parse_datetime(value)
    if parsed is None:
        date_only = parse_date(value)
        if date_only is None:
            return None
        parsed = datetime.combine(date_only, datetime.min.time())

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)

    return parsed


def _get_or_create_tag(name: str):
    name = name.strip()
    if not name:
        return None

    slug = slugify(name, allow_unicode=True) or hashlib.md5(name.encode('utf-8')).hexdigest()[:12]
    tag, _created = Tag.objects.get_or_create(
        slug=slug,
        defaults={'name': name[:50]},
    )
    return tag


@shared_task
def poll_source(source_id: str) -> str:
    """Опросить один источник и сохранить новые посты/события как RawItem."""
    try:
        source = Source.objects.get(id=source_id, is_active=True)
    except Source.DoesNotExist:
        return f'source {source_id} not found or inactive'

    collector = get_collector(source)
    if collector is None:
        return f'no collector for "{source.name}" (fetch_method={source.config.get("fetch_method")!r})'

    now = timezone.now()
    source.last_polled_at = now

    try:
        collected_items = collector.fetch(source)
    except Exception:
        logger.exception('Ошибка сбора источника "%s"', source.name)
        source.save(update_fields=['last_polled_at'])
        return f'"{source.name}": ошибка сбора'

    created = 0
    for item in collected_items:
        content_hash = _content_hash(item.raw_text)
        is_duplicate = RawItem.objects.filter(content_hash=content_hash).exists()

        _, was_created = RawItem.objects.get_or_create(
            source=source,
            external_id=item.external_id,
            defaults={
                'source_url': item.source_url,
                'published_at': item.published_at,
                'raw_text': item.raw_text,
                'raw_html': item.raw_payload,
                'media_urls': item.media_urls,
                'content_hash': content_hash,
                'status': RawItemStatus.DUPLICATE if is_duplicate else RawItemStatus.NEW,
            },
        )
        if was_created:
            created += 1

    source.last_success_at = now
    source.save(update_fields=['last_polled_at', 'last_success_at'])
    return f'"{source.name}": {created} new item(s)'


@shared_task
def poll_due_sources() -> str:
    """Запускается по расписанию Celery Beat: ставит в очередь источники, которые пора опросить."""
    now = timezone.now()
    queued = 0

    for source in Source.objects.filter(is_active=True):
        if get_collector(source) is None:
            continue
        if source.last_polled_at and now - source.last_polled_at < timedelta(minutes=source.poll_interval_minutes):
            continue
        poll_source.delay(str(source.id))
        queued += 1

    return f'queued {queued} source(s)'


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def classify_raw_item(self, raw_item_id: str) -> str:
    """Классифицирует RawItem через AI и создаёт Listing, если объявление релевантно."""
    try:
        raw_item = RawItem.objects.select_related('source').get(id=raw_item_id)
    except RawItem.DoesNotExist:
        return f'raw item {raw_item_id} not found'

    if raw_item.status != RawItemStatus.NEW:
        return f'raw item {raw_item_id}: already {raw_item.status}'

    if not classifier.looks_relevant(raw_item.raw_text):
        raw_item.status = RawItemStatus.SKIPPED
        raw_item.processed_at = timezone.now()
        raw_item.save(update_fields=['status', 'processed_at'])
        return f'raw item {raw_item_id}: skipped (keyword pre-filter)'

    try:
        result = classifier.classify_raw_item(raw_item)
    except Exception as exc:
        logger.exception('Ошибка AI-классификации RawItem %s', raw_item_id)
        raw_item.status = RawItemStatus.ERROR
        raw_item.error_message = str(exc)[:2000]
        raw_item.save(update_fields=['status', 'error_message'])
        raise self.retry(exc=exc)

    confidence = _clamp(result.get('confidence', 0), 0.0, 1.0)
    spam_score = _clamp(result.get('spam_score', 0), 0.0, 1.0)

    if not result.get('is_relevant') or spam_score >= settings.AGGREGATOR_SPAM_THRESHOLD:
        raw_item.status = RawItemStatus.SKIPPED
        raw_item.processed_at = timezone.now()
        raw_item.save(update_fields=['status', 'processed_at'])
        return (
            f'raw item {raw_item_id}: skipped '
            f'(is_relevant={result.get("is_relevant")}, spam_score={spam_score})'
        )

    listing_type = result.get('listing_type')
    if listing_type not in ListingType.values:
        listing_type = ListingType.OTHER

    source = raw_item.source
    auto_publish = (
        source.trust_level == SourceTrustLevel.TRUSTED
        and confidence >= settings.AGGREGATOR_AUTO_PUBLISH_CONFIDENCE
    )

    media_urls = raw_item.media_urls or []
    cover_image_url = media_urls[0] if media_urls and len(media_urls[0]) <= 200 else ''

    listing = Listing.objects.create(
        raw_item=raw_item,
        title=str(result.get('title') or raw_item.raw_text[:300])[:300],
        description=str(result.get('summary', '')),
        listing_type=listing_type,
        status=ListingStatus.PUBLISHED if auto_publish else ListingStatus.PENDING,
        organization_name=str(result.get('organization', ''))[:200],
        region=str(result.get('region', ''))[:100],
        is_online=bool(result.get('is_online', False)),
        start_date=_parse_ai_date(result.get('start_date')),
        application_deadline=_parse_ai_date(result.get('application_deadline')),
        source_url=raw_item.source_url,
        cover_image_url=cover_image_url,
        ai_confidence=confidence,
    )

    for tag_name in result.get('tags') or []:
        tag = _get_or_create_tag(str(tag_name))
        if tag:
            listing.tags.add(tag)

    raw_item.status = RawItemStatus.PROCESSED
    raw_item.processed_at = timezone.now()
    raw_item.save(update_fields=['status', 'processed_at'])

    return f'raw item {raw_item_id}: created listing {listing.id} ({listing.status})'


@shared_task
def classify_pending_items() -> str:
    """Запускается по расписанию: ставит в очередь новые RawItem на AI-классификацию."""
    raw_item_ids = list(
        RawItem.objects.filter(status=RawItemStatus.NEW)
        .order_by('fetched_at')
        .values_list('id', flat=True)[:CLASSIFY_BATCH_SIZE]
    )

    for raw_item_id in raw_item_ids:
        classify_raw_item.delay(str(raw_item_id))

    return f'queued {len(raw_item_ids)} item(s) for classification'


@shared_task
def auto_publish_and_cleanup() -> str:
    """Авто-публикация pending и удаление старых объявлений (90+ дней)."""
    from datetime import timedelta

    published = Listing.objects.filter(status=ListingStatus.PENDING).update(
        status=ListingStatus.PUBLISHED
    )

    cutoff = timezone.now() - timedelta(days=90)
    expired = Listing.objects.filter(created_at__lt=cutoff).update(
        status=ListingStatus.EXPIRED
    )

    return f'published {published}, expired {expired}'
