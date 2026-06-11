from django.contrib import admin

from .models import EventRecommendation


@admin.register(EventRecommendation)
class EventRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'match_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'event__title')
    readonly_fields = ('id', 'created_at')
