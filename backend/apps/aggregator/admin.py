from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Listing, RawItem, Source, Tag


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'source_type', 'identifier', 'trust_level',
        'is_active', 'poll_interval_minutes', 'last_success_at',
    )
    list_filter = ('source_type', 'trust_level', 'is_active')
    search_fields = ('name', 'identifier', 'url')
    ordering = ('name',)


@admin.register(RawItem)
class RawItemAdmin(admin.ModelAdmin):
    list_display = ('source', 'external_id', 'status', 'fetched_at', 'processed_at')
    list_filter = ('status', 'source')
    search_fields = ('raw_text', 'external_id', 'source_url')
    readonly_fields = ('content_hash', 'fetched_at')
    ordering = ('-fetched_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'listing_type', 'status', 'region', 'is_online',
        'application_deadline', 'ai_confidence', 'is_featured',
    )
    list_filter = ('status', 'listing_type', 'is_online', 'is_featured')
    search_fields = ('title', 'description', 'organization_name')
    autocomplete_fields = ('tags',)
    readonly_fields = ('raw_item', 'ai_confidence', 'created_at', 'updated_at')
    actions = ('approve_listings', 'reject_listings', 'mark_featured')

    @admin.action(description=_('Опубликовать выбранные'))
    def approve_listings(self, request, queryset):
        queryset.update(
            status='published',
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )

    @admin.action(description=_('Отклонить выбранные'))
    def reject_listings(self, request, queryset):
        queryset.update(
            status='rejected',
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )

    @admin.action(description=_('Отметить как рекомендуемые'))
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
