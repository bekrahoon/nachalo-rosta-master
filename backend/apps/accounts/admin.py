"""
Django Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, TokenBlacklist, UserSession, EmailTemplate


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom admin for CustomUser model"""
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'middle_name',
                'phone', 'date_of_birth', 'bio', 'avatar'
            )
        }),
        (_('Location'), {
            'fields': ('country', 'city', 'region')
        }),
        (_('Role and Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        (_('Email Verification'), {
            'fields': (
                'email_verified', 'email_verification_token',
                'email_verification_token_created'
            )
        }),
        (_('Password Reset'), {
            'fields': (
                'password_reset_token',
                'password_reset_token_created'
            )
        }),
        (_('Preferences'), {
            'fields': ('receive_emails', 'receive_notifications')
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at', 'updated_at', 'last_login_at'
            ),
            'classes': ('collapse',)
        }),
        (_('OAuth'), {
            'fields': ('google_id', 'github_id'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    list_display = (
        'email', 'get_full_name', 'role', 'email_verified',
        'is_active', 'created_at'
    )
    list_filter = ('role', 'email_verified', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login_at', 'id')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    """Admin for blacklisted tokens"""
    
    list_display = ('user', 'blacklisted_at')
    list_filter = ('blacklisted_at',)
    search_fields = ('user__email',)
    readonly_fields = ('blacklisted_at',)
    ordering = ('-blacklisted_at',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for user sessions"""
    
    list_display = ('user', 'ip_address', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('created_at', 'last_activity', 'token')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user', 'is_active')}),
        (_('Device Info'), {'fields': ('ip_address', 'user_agent', 'device_info')}),
        (_('Timestamps'), {'fields': ('created_at', 'last_activity')}),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin for email templates"""
    
    list_display = ('name', 'template_type', 'is_active', 'updated_at')
    list_filter = ('template_type', 'is_active')
    search_fields = ('name', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'template_type', 'is_active')}),
        (_('Email'), {'fields': ('subject', 'body')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
