from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class EventCategory(models.TextChoices):
    """Категории событий"""
    ENVIRONMENT = 'environment', _('Окружающая среда')
    EDUCATION = 'education', _('Образование')
    SOCIAL = 'social', _('Социальная помощь')
    HEALTH = 'health', _('Здравоохранение')
    CULTURE = 'culture', _('Культура и искусство')
    SPORTS = 'sports', _('Спорт и активный образ жизни')
    OTHER = 'other', _('Другое')


class EventStatus(models.TextChoices):
    """Статусы события"""
    DRAFT = 'draft', _('Черновик')
    UPCOMING = 'upcoming', _('Предстоящее')
    ONGOING = 'ongoing', _('В процессе')
    COMPLETED = 'completed', _('Завершено')
    CANCELLED = 'cancelled', _('Отменено')


class Event(models.Model):
    """Модель волонтёрского события"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Основная информация
    title = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'))
    category = models.CharField(
        _('категория'),
        max_length=20,
        choices=EventCategory.choices,
        default=EventCategory.OTHER
    )
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT
    )
    
    # Организатор
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name=_('организатор'),
        limit_choices_to={'role__in': ['organizer', 'admin']}
    )
    
    # Место и время
    start_date = models.DateTimeField(_('дата начала'))
    end_date = models.DateTimeField(_('дата окончания'))
    location = models.CharField(_('место проведения'), max_length=200)
    latitude = models.DecimalField(
        _('широта'), max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        _('долгота'), max_digits=9, decimal_places=6, null=True, blank=True
    )
    
    # Волонтёры
    max_volunteers = models.IntegerField(
        _('максимум волонтёров'),
        validators=[MinValueValidator(1)],
        default=10
    )
    volunteers = models.ManyToManyField(
        User,
        through='EventVolunteer',
        related_name='participated_events',
        verbose_name=_('волонтёры'),
        blank=True
    )
    
    # Требования
    required_skills = models.TextField(
        _('требуемые навыки'),
        blank=True,
        help_text='Разделите запятыми'
    )
    volunteer_hours = models.FloatField(
        _('часы волонтёрства'),
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Сколько часов получит каждый волонтёр'
    )
    
    # Описание и контакт
    contact_person = models.CharField(_('контактное лицо'), max_length=100, blank=True)
    contact_phone = models.CharField(_('контактный телефон'), max_length=20, blank=True)
    contact_email = models.EmailField(_('контактный email'), blank=True)
    
    # Изображение
    image = models.ImageField(
        _('изображение'),
        upload_to='events/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    # Метаданные
    is_featured = models.BooleanField(_('рекомендуемое'), default=False)
    is_online = models.BooleanField(_('онлайн событие'), default=False)
    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('событие')
        verbose_name_plural = _('события')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['organizer']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
    
    @property
    def is_full(self):
        """Проверка заполнено ли событие"""
        return self.eventvolunteer_set.count() >= self.max_volunteers
    
    @property
    def available_slots(self):
        """Количество свободных мест"""
        return self.max_volunteers - self.eventvolunteer_set.count()
    
    @property
    def total_volunteers(self):
        """Всего волонтёров"""
        return self.eventvolunteer_set.count()


class EventVolunteer(models.Model):
    """Модель участия волонтёра в событии"""
    
    VOLUNTEER_STATUS = (
        ('applied', _('Заявился')),
        ('approved', _('Одобрено')),
        ('completed', _('Завершено')),
        ('cancelled', _('Отменено')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('событие')
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('волонтёр')
    )
    
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=VOLUNTEER_STATUS,
        default='applied'
    )
    
    hours_completed = models.FloatField(
        _('завершённые часы'),
        validators=[MinValueValidator(0)],
        default=0
    )
    
    applied_at = models.DateTimeField(_('дата заявки'), auto_now_add=True)
    joined_at = models.DateTimeField(_('дата присоединения'), null=True, blank=True)
    completed_at = models.DateTimeField(_('дата завершения'), null=True, blank=True)
    
    # Рейтинг и отзыв
    rating = models.IntegerField(
        _('рейтинг'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True
    )
    feedback = models.TextField(_('отзыв'), blank=True)
    
    class Meta:
        verbose_name = _('участие волонтёра')
        verbose_name_plural = _('участия волонтёров')
        unique_together = ('event', 'volunteer')
        ordering = ['-applied_at']
    
    def __str__(self):
        return f'{self.volunteer.email} - {self.event.title}'


class EventRating(models.Model):
    """Модель оценки события волонтёром"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('событие')
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('волонтёр')
    )
    
    rating = models.IntegerField(
        _('оценка'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_('комментарий'), blank=True)
    
    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('оценка события')
        verbose_name_plural = _('оценки событий')
        unique_together = ('event', 'volunteer')
    
    def __str__(self):
        return f'{self.volunteer.email} - {self.event.title} - {self.rating}★'
