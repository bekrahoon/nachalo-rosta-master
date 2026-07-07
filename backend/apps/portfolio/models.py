from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class PortfolioProfile(models.Model):
    """Настройки отображения портфолио волонтёра"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_profile',
        verbose_name=_('пользователь'),
    )

    title = models.CharField(_('заголовок портфолио'), max_length=200, blank=True)
    description = models.TextField(_('описание'), blank=True)
    is_public = models.BooleanField(_('показывать личные данные'), default=True)

    updated_at = models.DateTimeField(_('обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('профиль портфолио')
        verbose_name_plural = _('профили портфолио')

    def __str__(self):
        return f'Портфолио {self.user.email}'


class SavedListing(models.Model):
    """Сохранённая пользователем возможность из агрегатора"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_listings',
        verbose_name=_('пользователь'),
    )
    listing = models.ForeignKey(
        'aggregator.Listing',
        on_delete=models.CASCADE,
        related_name='saved_by',
        verbose_name=_('объявление'),
    )

    created_at = models.DateTimeField(_('сохранено'), auto_now_add=True)

    class Meta:
        verbose_name = _('сохранённая программа')
        verbose_name_plural = _('сохранённые программы')
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} -> {self.listing.title}'
