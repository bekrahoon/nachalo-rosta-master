from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Event, EventVolunteer, EventRating


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin для Event"""
    
    list_display = (
        'title', 'category', 'status', 'organizer',
        'start_date', 'total_volunteers', 'max_volunteers', 'is_featured'
    )
    list_filter = ('category', 'status', 'is_online', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'organizer__email', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'title', 'description', 'category', 'status')
        }),
        (_('Организатор'), {
            'fields': ('organizer',)
        }),
        (_('Место и время'), {
            'fields': ('start_date', 'end_date', 'location', 'latitude', 'longitude', 'is_online')
        }),
        (_('Волонтёры'), {
            'fields': ('max_volunteers', 'required_skills', 'volunteer_hours')
        }),
        (_('Контакты'), {
            'fields': ('contact_person', 'contact_phone', 'contact_email')
        }),
        (_('Медиа'), {
            'fields': ('image',)
        }),
        (_('Опции'), {
            'fields': ('is_featured',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_volunteers(self, obj):
        return obj.total_volunteers
    total_volunteers.short_description = _('Волонтёров')


@admin.register(EventVolunteer)
class EventVolunteerAdmin(admin.ModelAdmin):
    """Admin для EventVolunteer"""
    
    list_display = (
        'volunteer', 'event', 'status', 'hours_completed',
        'applied_at', 'joined_at', 'rating'
    )
    list_filter = ('status', 'applied_at', 'rating')
    search_fields = ('event__title', 'volunteer__email')
    readonly_fields = ('id', 'applied_at')
    
    fieldsets = (
        (_('Информация'), {
            'fields': ('id', 'event', 'volunteer', 'status')
        }),
        (_('Часы и оценка'), {
            'fields': ('hours_completed', 'rating', 'feedback')
        }),
        (_('Даты'), {
            'fields': ('applied_at', 'joined_at', 'completed_at')
        }),
    )


@admin.register(EventRating)
class EventRatingAdmin(admin.ModelAdmin):
    """Admin для EventRating"""
    
    list_display = ('volunteer', 'event', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('event__title', 'volunteer__email', 'comment')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        (_('Информация'), {
            'fields': ('id', 'event', 'volunteer')
        }),
        (_('Оценка'), {
            'fields': ('rating', 'comment')
        }),
        (_('Дата'), {
            'fields': ('created_at',)
        }),
    )
