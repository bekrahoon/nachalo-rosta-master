from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Badge, UserBadge, Level, Stats


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin для Badge"""
    
    list_display = ('name', 'icon', 'criteria_type', 'criteria_value', 'points', 'rarity', 'created_at')
    list_filter = ('rarity', 'criteria_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'name', 'description', 'icon', 'icon_url')
        }),
        (_('Условия'), {
            'fields': ('condition', 'criteria_type', 'criteria_value')
        }),
        (_('Статистика'), {
            'fields': ('points', 'rarity')
        }),
        (_('Метаданные'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin для UserBadge"""
    
    list_display = ('user', 'badge', 'unlocked_at')
    list_filter = ('badge', 'unlocked_at')
    search_fields = ('user__email', 'badge__name')
    readonly_fields = ('id', 'unlocked_at')
    
    fieldsets = (
        (_('Информация'), {
            'fields': ('id', 'user', 'badge')
        }),
        (_('Дата'), {
            'fields': ('unlocked_at',)
        }),
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin для Level"""
    
    list_display = ('name', 'icon', 'min_points', 'max_points', 'color')
    list_filter = ('min_points',)
    search_fields = ('name',)
    readonly_fields = ('id',)


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    """Admin для Stats"""
    
    list_display = ('user', 'total_points', 'level', 'total_hours', 'total_events')
    list_filter = ('level', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'updated_at')
    
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('id', 'user')
        }),
        (_('Волонтёрство'), {
            'fields': ('total_hours', 'total_events', 'total_teams')
        }),
        (_('Рейтинг'), {
            'fields': ('total_points', 'level')
        }),
        (_('Лучший месяц'), {
            'fields': ('best_month_hours', 'best_month')
        }),
        (_('Метаданные'), {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
