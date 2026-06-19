from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid

from apps.aggregator.models import Listing
from apps.events.models import Event

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
    requirements = models.TextField(_('требования'), blank=True, default='')
    max_members = models.PositiveIntegerField(
        _('макс. участников'),
        null=True,
        blank=True,
        validators=[MinValueValidator(2)],
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teamups',
        verbose_name=_('возможность'),
    )

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


class RecruitmentSlot(models.Model):
    """Объявление о наборе волонтёров от команды на конкретное событие"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='recruitment_slots',
        verbose_name=_('команда'),
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='recruitment_slots',
        verbose_name=_('событие'),
    )
    description = models.TextField(_('описание'), blank=True)
    slots_available = models.PositiveIntegerField(
        _('доступно мест'),
        validators=[MinValueValidator(1)],
        default=1,
    )
    is_open = models.BooleanField(_('открыт набор'), default=True)

    created_at = models.DateTimeField(_('создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('набор волонтёров')
        verbose_name_plural = _('наборы волонтёров')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.team.name} -> {self.event.title}'

    @property
    def approved_count(self):
        return self.applications.filter(status=TeamApplicationStatus.APPROVED).count()

    @property
    def remaining_slots(self):
        return max(self.slots_available - self.approved_count, 0)


class TeamApplicationStatus(models.TextChoices):
    """Статусы заявки на участие в наборе"""
    PENDING = 'pending', _('На рассмотрении')
    APPROVED = 'approved', _('Одобрено')
    REJECTED = 'rejected', _('Отклонено')


class TeamApplication(models.Model):
    """Заявка пользователя на участие в наборе волонтёров команды"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slot = models.ForeignKey(
        RecruitmentSlot,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('набор'),
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_applications',
        verbose_name=_('заявитель'),
    )
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=TeamApplicationStatus.choices,
        default=TeamApplicationStatus.PENDING,
    )
    message = models.TextField(_('сообщение'), blank=True)

    applied_at = models.DateTimeField(_('подано'), auto_now_add=True)
    reviewed_at = models.DateTimeField(_('рассмотрено'), null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_team_applications',
        verbose_name=_('рассмотрено кем'),
    )

    class Meta:
        verbose_name = _('заявка на участие')
        verbose_name_plural = _('заявки на участие')
        unique_together = ('slot', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.applicant.email} -> {self.slot} ({self.get_status_display()})'
