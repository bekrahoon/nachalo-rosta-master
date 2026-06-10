from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class Badge(models.Model):
    """Модель достижения/бейджа"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Основная информация
    name = models.CharField(_('название'), max_length=100, unique=True)
    description = models.TextField(_('описание'))
    icon = models.CharField(
        _('иконка (emoji)'),
        max_length=10,
        default='🏆',
        help_text='Emoji или путь к изображению'
    )
    
    # Условия получения
    condition = models.CharField(
        _('условие получения'),
        max_length=100,
        help_text='Описание как получить это достижение'
    )
    
    # Статистика
    points = models.IntegerField(_('баллы'), default=10)
    rarity = models.CharField(
        _('редкость'),
        max_length=20,
        choices=[
            ('common', _('Обычное')),
            ('uncommon', _('Редкое')),
            ('rare', _('Очень редкое')),
            ('legendary', _('Легендарное')),
        ],
        default='common'
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('достижение')
        verbose_name_plural = _('достижения')
        ordering = ['-points']
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Модель достижения пользователя"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges',
        verbose_name=_('пользователь')
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        verbose_name=_('достижение')
    )
    
    unlocked_at = models.DateTimeField(_('получено'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('достижение пользователя')
        verbose_name_plural = _('достижения пользователя')
        unique_together = ('user', 'badge')
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.badge.name}'


class Level(models.Model):
    """Модель уровня волонтёра"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(_('название'), max_length=100)
    icon = models.CharField(_('иконка'), max_length=10, default='🌟')
    
    min_points = models.IntegerField(_('минимум баллов'))
    max_points = models.IntegerField(_('максимум баллов'), null=True, blank=True)
    
    color = models.CharField(
        _('цвет'),
        max_length=7,
        default='#6366f1',
        help_text='HEX код цвета'
    )
    
    class Meta:
        verbose_name = _('уровень')
        verbose_name_plural = _('уровни')
        ordering = ['min_points']
    
    def __str__(self):
        return f'{self.name} ({self.min_points}+ баллов)'


class Stats(models.Model):
    """Модель статистики пользователя"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name=_('пользователь')
    )
    
    # Статистика волонтёрства
    total_hours = models.FloatField(_('всего часов'), default=0)
    total_events = models.IntegerField(_('всего событий'), default=0)
    total_teams = models.IntegerField(_('всего команд'), default=0)
    
    # Рейтинг и уровень
    total_points = models.IntegerField(_('всего баллов'), default=0)
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('уровень')
    )
    
    # Лучший месяц
    best_month_hours = models.FloatField(_('часов в лучший месяц'), default=0)
    best_month = models.CharField(_('лучший месяц'), max_length=7, blank=True)
    
    # Метаданные
    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('статистика')
        verbose_name_plural = _('статистики')
    
    def __str__(self):
        return f'Статистика {self.user.email}'
