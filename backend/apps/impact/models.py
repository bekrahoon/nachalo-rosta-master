from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid

from apps.events.models import Event

User = get_user_model()


class ImpactRecord(models.Model):
    """Запись социального воздействия волонтёра"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='impact_records',
        verbose_name=_('пользователь'),
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impact_records',
        verbose_name=_('событие'),
    )

    hours_contributed = models.FloatField(
        _('часов внесено'),
        validators=[MinValueValidator(0)],
        default=0,
    )
    funds_raised_or_equivalent = models.DecimalField(
        _('собрано средств (или эквивалент)'),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Сумма собранных средств или денежный эквивалент вклада'),
    )

    recorded_at = models.DateTimeField(_('дата записи'), default=timezone.now)

    class Meta:
        verbose_name = _('запись воздействия')
        verbose_name_plural = _('записи воздействия')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', '-recorded_at']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.hours_contributed}ч - {self.recorded_at:%Y-%m-%d}'
