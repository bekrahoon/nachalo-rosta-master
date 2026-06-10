"""
Views for user authentication and account management.
"""

from rest_framework import viewsets, status, views, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import secrets
from datetime import timedelta

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    EmailVerificationSerializer, PasswordResetRequestSerializer,
    PasswordResetSerializer, ChangePasswordSerializer,
    UserUpdateSerializer, LogoutSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOrganizerOrAdmin
from .tasks import send_password_reset_email

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that returns user info with tokens.
    """
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            # Log failed login attempt
            email = request.data.get('email', '').lower()
            cache_key = f'login_attempts:{email}'
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, 3600)  # 1 hour
            
            if attempts > 5:
                return Response(
                    {'detail': _('Too many login attempts. Please try again later.')},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            raise
        
        # Clear login attempts on successful login
        email = request.data.get('email', '').lower()
        cache.delete(f'login_attempts:{email}')
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(views.APIView):
    """
    User registration endpoint.
    POST: Register new user
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register new user with email verification"""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': _('Registration successful. Please check your email to verify your account.'),
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(views.APIView):
    """
    Email verification endpoint.
    POST: Verify email with token
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Verify email using token"""
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.user
            user.activate_email()
            
            return Response(
                {
                    'message': _('Email verified successfully. You can now log in.'),
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(views.APIView):
    """
    Resend email verification token.
    POST: Resend verification email
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Resend verification email"""
        email = request.data.get('email', '').lower()
        
        try:
            user = User.objects.get(email=email, email_verified=False)
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            return Response(
                {'message': _('If the email exists and is not verified, a verification email will be sent.')},
                status=status.HTTP_200_OK
            )
        
        # Generate new token
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.email_verification_token_created = timezone.now()
        user.save(update_fields=[
            'email_verification_token',
            'email_verification_token_created'
        ])
        
        # Send verification email
        from apps.accounts.tasks import send_email_verification
        send_email_verification.delay(user.id)
        
        return Response(
            {'message': _('Verification email has been sent.')},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(views.APIView):
    """
    Password reset request endpoint.
    POST: Request password reset (send email)
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Request password reset"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = secrets.token_urlsafe(32)
                user.password_reset_token = token
                user.password_reset_token_created = timezone.now()
                user.save(update_fields=[
                    'password_reset_token',
                    'password_reset_token_created'
                ])
                
                # Send reset email
                send_password_reset_email.delay(user.id)
            except User.DoesNotExist:
                pass
            
            # For security, always return same message
            return Response(
                {
                    'message': _('If the email exists, a password reset link will be sent.')
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(views.APIView):
    """
    Password reset confirmation endpoint.
    POST: Reset password with token
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Reset password"""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': _('Password reset successful. You can now log in with your new password.'),
                    'email': user.email
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """
    Logout endpoint - blacklist refresh token.
    POST: Logout user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user by blacklisting refresh token"""
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data.get('refresh')
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
            except Exception:
                pass
            
            return Response(
                {'message': _('Successfully logged out.')},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    """
    User profile endpoint.
    GET: Get current user profile
    PUT: Update current user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': _('Profile updated successfully.'),
                    'user': UserSerializer(request.user).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(views.APIView):
    """
    Change password endpoint.
    POST: Change password (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change password"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': _('Password changed successfully.')},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(views.APIView):
    """
    Get user by ID (public endpoint).
    GET: Get user public profile
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """Get user public profile"""
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': _('User not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return limited public info
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyTokenView(views.APIView):
    """
    Verify if token is valid.
    POST: Verify token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify token is still valid"""
        return Response(
            {
                'valid': True,
                'user': UserSerializer(request.user).data
            },
            status=status.HTTP_200_OK
        )


class UserCheckEmailView(views.APIView):
    """
    Check if email is available.
    POST: Check email availability
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Check if email is available for registration"""
        email = request.data.get('email', '').lower()
        
        if not email:
            return Response(
                {'available': False, 'error': _('Email is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = User.objects.filter(email=email).exists()
        
        return Response(
            {'available': not exists},
            status=status.HTTP_200_OK
        )
