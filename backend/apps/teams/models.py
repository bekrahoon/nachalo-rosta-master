from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class TeamRole(models.TextChoices):
    """Роли в команде"""
    LEADER = 'leader', _('Лидер')
    MEMBER = 'member', _('Член')
    MODERATOR = 'moderator', _('Модератор')


class TeamStatus(models.TextChoices):
    """Статусы команды"""
    ACTIVE = 'active', _('Активная')
    INACTIVE = 'inactive', _('Неактивная')
    ARCHIVED = 'archived', _('Архивирована')


class Team(models.Model):
    """Модель команды волонтёров"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Основная информация
    name = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'))
    
    # Лидер
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='led_teams',
        verbose_name=_('лидер')
    )
    
    # Члены команды
    members = models.ManyToManyField(
        User,
        through='TeamMember',
        related_name='teams',
        verbose_name=_('члены')
    )
    
    # Информация
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=TeamStatus.choices,
        default=TeamStatus.ACTIVE
    )
    avatar = models.ImageField(
        _('аватар'),
        upload_to='teams/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    # Статистика
    total_hours = models.FloatField(_('всего часов'), default=0)
    total_volunteers = models.IntegerField(_('всего волонтёров'), default=0)
    
    # Метаданные
    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('команда')
        verbose_name_plural = _('команды')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Модель члена команды"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name=_('команда')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('пользователь')
    )
    
    role = models.CharField(
        _('роль'),
        max_length=20,
        choices=TeamRole.choices,
        default=TeamRole.MEMBER
    )
    
    joined_at = models.DateTimeField(_('присоединился'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('член команды')
        verbose_name_plural = _('члены команды')
        unique_together = ('team', 'user')
        ordering = ['-joined_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.team.name} ({self.get_role_display()})'
