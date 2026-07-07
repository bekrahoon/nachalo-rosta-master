from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import RecruitmentSlot, Team, TeamApplication, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin для Team"""
    
    list_display = ('name', 'leader', 'status', 'total_volunteers', 'total_hours', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'leader__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'name', 'description')
        }),
        (_('Лидер'), {
            'fields': ('leader',)
        }),
        (_('Статус'), {
            'fields': ('status',)
        }),
        (_('Медиа'), {
            'fields': ('avatar',)
        }),
        (_('Статистика'), {
            'fields': ('total_hours', 'total_volunteers')
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin для TeamMember"""
    
    list_display = ('user', 'team', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('team__name', 'user__email')
    readonly_fields = ('id', 'joined_at')
    
    fieldsets = (
        (_('Информация'), {
            'fields': ('id', 'team', 'user')
        }),
        (_('Роль'), {
            'fields': ('role',)
        }),
        (_('Дата'), {
            'fields': ('joined_at',)
        }),
    )


@admin.register(RecruitmentSlot)
class RecruitmentSlotAdmin(admin.ModelAdmin):
    """Admin для RecruitmentSlot"""

    list_display = ('team', 'event', 'slots_available', 'is_open', 'created_at')
    list_filter = ('is_open', 'created_at')
    search_fields = ('team__name', 'event__title')
    readonly_fields = ('id', 'created_at')


@admin.register(TeamApplication)
class TeamApplicationAdmin(admin.ModelAdmin):
    """Admin для TeamApplication"""

    list_display = ('applicant', 'slot', 'status', 'applied_at', 'reviewed_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__email', 'slot__team__name')
    readonly_fields = ('id', 'applied_at')
