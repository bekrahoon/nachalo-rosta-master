from django.contrib import admin

from .models import ImpactRecord


@admin.register(ImpactRecord)
class ImpactRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'hours_contributed', 'funds_raised_or_equivalent', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('user__email', 'event__title')
    readonly_fields = ('id', 'recorded_at')
