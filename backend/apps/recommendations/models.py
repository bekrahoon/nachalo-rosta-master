from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

from apps.aggregator.models import Listing

User = get_user_model()


class EventRecommendation(models.Model):
    """AI-сгенерированная рекомендация объявления для пользователя"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('пользователь'),
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('объявление'),
    )

    match_score = models.FloatField(
        _('оценка соответствия'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Процент соответствия интересам/навыкам пользователя (0-100)'),
    )
    reason = models.TextField(_('причина рекомендации'), blank=True)

    created_at = models.DateTimeField(_('создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('рекомендация объявления')
        verbose_name_plural = _('рекомендации объявлений')
        unique_together = ('user', 'listing')
        ordering = ['-match_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-match_score']),
        ]

    def __str__(self):
        return f'{self.user.email} -> {self.listing.title} ({self.match_score}%)'
