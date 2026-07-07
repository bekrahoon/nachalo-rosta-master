"""
Serializers for user authentication and account management.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    is_organizer = serializers.BooleanField(read_only=True)
    is_moderator = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'middle_name',
            'full_name', 'short_name', 'phone', 'bio', 'avatar',
            'date_of_birth', 'country', 'city', 'region',
            'role', 'status_label', 'email_verified', 'is_organizer', 'is_moderator',
            'created_at', 'updated_at', 'last_login_at',
            'receive_emails', 'receive_notifications',
            'interests', 'skills'
        ]
        read_only_fields = [
            'id', 'email_verified', 'created_at', 'updated_at', 'last_login_at'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=12,
        help_text=_('Password must be at least 12 characters long.')
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label=_('Confirm password')
    )
    first_name = serializers.CharField(required=True, min_length=2)
    last_name = serializers.CharField(required=True, min_length=2)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate_email(self, value):
        """Check if email is not already registered"""
        if User.objects.filter(email=value).exists():
            raise ValidationError(_('This email is already registered.'))
        return value.lower()
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise ValidationError({'password': _('Passwords do not match.')})
        return attrs
    
    def create(self, validated_data):
        """Create new user, active immediately (no email verification for MVP)"""
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            is_active=True,
            email_verified=True,
        )

        # Hash and set password
        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('Invalid credentials.'))
        
        if not user.check_password(password):
            raise ValidationError(_('Invalid credentials.'))

        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user exists"""
        try:
            User.objects.get(email=value.lower())
        except User.DoesNotExist:
            # For security, we don't reveal whether email exists
            pass
        return value.lower()


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    token = serializers.CharField()
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        min_length=12,
        help_text=_('Password must be at least 12 characters long.')
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        label=_('Confirm password')
    )
    
    def validate_new_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['new_password'] != attrs.pop('new_password_confirm'):
            raise ValidationError({'new_password': _('Passwords do not match.')})
        
        # Validate reset token
        token = attrs['token']
        try:
            user = User.objects.get(password_reset_token=token)
            
            # Check if token is not expired (1 hour)
            if user.password_reset_token_created:
                token_age = timezone.now() - user.password_reset_token_created
                if token_age > timedelta(hours=1):
                    raise ValidationError(_('Password reset token has expired.'))
            
            self.user = user
        except User.DoesNotExist:
            raise ValidationError(_('Invalid or expired password reset token.'))
        
        return attrs
    
    def save(self):
        """Save new password"""
        user = self.user
        user.set_password(self.validated_data['new_password'])
        user.password_reset_token = None
        user.password_reset_token_created = None
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users)"""
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        min_length=12
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Verify old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError(_('Current password is incorrect.'))
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match"""
        if attrs['new_password'] != attrs.pop('new_password_confirm'):
            raise ValidationError({'new_password': _('Passwords do not match.')})
        return attrs
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone',
            'bio', 'avatar', 'date_of_birth',
            'country', 'city', 'region', 'status_label',
            'receive_emails', 'receive_notifications',
            'interests', 'skills'
        ]


class TokenRefreshResponseSerializer(serializers.Serializer):
    """Serializer for token refresh response"""
    access = serializers.CharField()
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout (blacklist token)"""
    refresh = serializers.CharField(required=False)
