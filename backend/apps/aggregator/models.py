from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class SourceType(models.TextChoices):
    """Тип источника данных"""
    TELEGRAM = 'telegram', _('Telegram-канал')
    VK = 'vk', _('VK-паблик')
    WEBSITE = 'website', _('Сайт / API')
    DISCORD = 'discord', _('Discord')
    RSS = 'rss', _('RSS-фид')
    MANUAL = 'manual', _('Ручной ввод')


class SourceTrustLevel(models.TextChoices):
    """Уровень доверия источнику"""
    QUARANTINE = 'quarantine', _('Карантин (всё на модерацию)')
    TRUSTED = 'trusted', _('Доверенный (авто-публикация при высокой уверенности AI)')


class Source(models.Model):
    """Источник данных для сбора объявлений"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_('название'), max_length=150)
    source_type = models.CharField(
        _('тип источника'),
        max_length=20,
        choices=SourceType.choices,
    )
    identifier = models.CharField(
        _('идентификатор'),
        max_length=255,
        help_text='Username Telegram-канала, screen_name паблика VK или URL/эндпоинт для сайта'
    )
    url = models.URLField(_('ссылка на источник'), blank=True)

    trust_level = models.CharField(
        _('уровень доверия'),
        max_length=20,
        choices=SourceTrustLevel.choices,
        default=SourceTrustLevel.QUARANTINE,
    )
    is_active = models.BooleanField(_('активен'), default=True)
    poll_interval_minutes = models.PositiveIntegerField(
        _('интервал опроса (мин)'),
        default=120,
    )
    config = models.JSONField(
        _('доп. настройки'),
        default=dict,
        blank=True,
        help_text='Специфичные для источника параметры (категории, лимиты и т.п.)'
    )
    notes = models.TextField(_('заметки'), blank=True)

    last_polled_at = models.DateTimeField(_('последний опрос'), null=True, blank=True)
    last_success_at = models.DateTimeField(_('последний успешный сбор'), null=True, blank=True)

    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('источник')
        verbose_name_plural = _('источники')
        ordering = ['name']
        indexes = [
            models.Index(fields=['source_type', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_source_type_display()})'


class RawItemStatus(models.TextChoices):
    """Статус обработки сырого элемента"""
    NEW = 'new', _('Новый')
    PROCESSED = 'processed', _('Обработан')
    DUPLICATE = 'duplicate', _('Дубликат')
    SKIPPED = 'skipped', _('Отфильтрован')
    ERROR = 'error', _('Ошибка')


class RawItem(models.Model):
    """Сырые данные, собранные из источника, до AI-классификации"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='raw_items',
        verbose_name=_('источник'),
    )
    external_id = models.CharField(
        _('внешний ID'),
        max_length=255,
        help_text='ID сообщения/поста в источнике'
    )
    source_url = models.URLField(_('ссылка на оригинал'), blank=True)
    published_at = models.DateTimeField(_('опубликовано в источнике'), null=True, blank=True)

    raw_text = models.TextField(_('текст'), blank=True)
    raw_html = models.TextField(_('HTML'), blank=True)
    media_urls = models.JSONField(_('медиа'), default=list, blank=True)

    content_hash = models.CharField(_('хэш контента'), max_length=64, db_index=True)
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=RawItemStatus.choices,
        default=RawItemStatus.NEW,
    )
    error_message = models.TextField(_('сообщение об ошибке'), blank=True)

    fetched_at = models.DateTimeField(_('собрано'), auto_now_add=True)
    processed_at = models.DateTimeField(_('обработано'), null=True, blank=True)

    class Meta:
        verbose_name = _('сырой элемент')
        verbose_name_plural = _('сырые элементы')
        ordering = ['-fetched_at']
        unique_together = ('source', 'external_id')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return f'{self.source.name} / {self.external_id}'


class ListingType(models.TextChoices):
    """Тип объявления о возможности"""
    HACKATHON = 'hackathon', _('Хакатон')
    GRANT = 'grant', _('Грант / Стипендия')
    INTERNSHIP = 'internship', _('Стажировка')
    CONTEST = 'contest', _('Конкурс')
    COURSE = 'course', _('Курс / Обучение')
    OTHER = 'other', _('Другое')


class ListingStatus(models.TextChoices):
    """Статус объявления в каталоге"""
    PENDING = 'pending', _('На модерации')
    PUBLISHED = 'published', _('Опубликовано')
    REJECTED = 'rejected', _('Отклонено')
    EXPIRED = 'expired', _('Истекло')


class Tag(models.Model):
    """Тег для объявлений"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), max_length=60, unique=True)

    class Meta:
        verbose_name = _('тег')
        verbose_name_plural = _('теги')
        ordering = ['name']

    def __str__(self):
        return self.name


class Listing(models.Model):
    """Объявление о возможности (волонтёрство, хакатон, грант, форум и т.п.)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    raw_item = models.ForeignKey(
        RawItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listings',
        verbose_name=_('сырой элемент'),
    )

    title = models.CharField(_('название'), max_length=300)
    description = models.TextField(_('описание'), blank=True)
    listing_type = models.CharField(
        _('тип'),
        max_length=20,
        choices=ListingType.choices,
        default=ListingType.OTHER,
    )
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=ListingStatus.choices,
        default=ListingStatus.PENDING,
    )

    organization_name = models.CharField(_('организация'), max_length=200, blank=True)
    region = models.CharField(_('регион'), max_length=100, blank=True)
    is_online = models.BooleanField(_('онлайн'), default=False)

    start_date = models.DateTimeField(_('дата начала'), null=True, blank=True)
    end_date = models.DateTimeField(_('дата окончания'), null=True, blank=True)
    application_deadline = models.DateTimeField(_('дедлайн заявки'), null=True, blank=True)

    source_url = models.URLField(_('ссылка на источник'), blank=True)
    cover_image_url = models.URLField(_('обложка'), blank=True)

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='listings',
        verbose_name=_('теги'),
    )

    ai_confidence = models.FloatField(
        _('уверенность AI'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    is_featured = models.BooleanField(_('рекомендуемое'), default=False)

    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_listings',
        verbose_name=_('модератор'),
    )
    moderated_at = models.DateTimeField(_('дата модерации'), null=True, blank=True)
    moderation_notes = models.TextField(_('заметки модератора'), blank=True)

    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('объявление')
        verbose_name_plural = _('объявления')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'application_deadline']),
            models.Index(fields=['listing_type']),
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
