"""
Custom User model and related models for authentication and authorization.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid


class CustomUserManager(UserManager):
    """Custom manager для CustomUser"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError(_('Email is required'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
    """User roles for Nachalo Rosta"""
    USER = 'user', _('Волонтёр')
    ORGANIZER = 'organizer', _('Организатор')
    ADMIN = 'admin', _('Администратор')
    MODERATOR = 'moderator', _('Модератор')


class CustomUser(AbstractUser):
    """
    Custom User model with email authentication.
    Roles: user (volunteer), organizer, admin, moderator.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Phone number must be entered in the format: +999999999. Up to 15 digits allowed.')
            )
        ]
    )
    
    # Profile information
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=150, blank=True)
    bio = models.TextField(_('biography'), blank=True, null=True, max_length=500)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    
    # Location
    country = models.CharField(_('country'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    region = models.CharField(_('region/state'), max_length=100, blank=True)
    
    # Roles and permissions
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    
    # Email verification
    email_verified = models.BooleanField(_('email verified'), default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email_verification_token_created = models.DateTimeField(blank=True, null=True)
    
    # Password reset
    password_reset_token = models.CharField(max_length=255, blank=True, null=True, unique=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)
    
    # Status and timestamps
    is_active = models.BooleanField(_('active'), default=False)  # Not active until email is verified
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_login_at = models.DateTimeField(_('last login'), blank=True, null=True)
    
    # Preferences
    receive_emails = models.BooleanField(_('receive emails'), default=True)
    receive_notifications = models.BooleanField(_('receive notifications'), default=True)

    # Volunteering profile (used for AI recommendations matching)
    interests = models.JSONField(
        _('interests'),
        default=list,
        blank=True,
        help_text=_('List of volunteering interest categories, e.g. ["education", "environment"]')
    )
    skills = models.JSONField(
        _('skills'),
        default=list,
        blank=True,
        help_text=_('List of skills, e.g. ["first aid", "photography", "teaching"]')
    )
    
    # OAuth fields (for future social auth)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    github_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Required fields when creating via createsuperuser
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'
    
    def get_full_name(self):
        """Return the user's full name."""
        if self.middle_name:
            return f'{self.first_name} {self.middle_name} {self.last_name}'.strip()
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_organizer(self):
        """Check if user is organizer or admin"""
        return self.role in [UserRole.ORGANIZER, UserRole.ADMIN]
    
    @property
    def is_moderator(self):
        """Check if user is moderator or admin"""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN]
    
    def activate_email(self):
        """Mark email as verified and activate account"""
        self.email_verified = True
        self.is_active = True
        self.email_verification_token = None
        self.email_verification_token_created = None
        self.save(update_fields=[
            'email_verified', 'is_active', 
            'email_verification_token', 'email_verification_token_created'
        ])


class TokenBlacklist(models.Model):
    """
    Model for storing blacklisted tokens (for logout).
    Works with djangorestframework-simplejwt.
    """
    token = models.TextField(unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Blacklisted Token')
        verbose_name_plural = _('Blacklisted Tokens')
        ordering = ['-blacklisted_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.blacklisted_at}'


class UserSession(models.Model):
    """
    Track user sessions for security monitoring.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    token = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.ip_address} - {self.created_at}'


class EmailTemplate(models.Model):
    """
    Store email templates for various notifications.
    """
    TEMPLATE_TYPES = (
        ('verification', _('Email Verification')),
        ('password_reset', _('Password Reset')),
        ('welcome', _('Welcome Email')),
        ('notification', _('Notification')),
        ('achievement', _('Achievement Unlock')),
    )
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
    
    def __str__(self):
        return self.name
