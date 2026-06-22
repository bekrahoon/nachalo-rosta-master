"""
URL configuration for accounts app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    PasswordResetRequestView,
    PasswordResetView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    UserDetailView,
    VerifyTokenView,
    UserCheckEmailView,
)
from .social_auth import SocialAuthView, SocialAuthConfigView

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Social OAuth
    path('social/<str:provider>/', SocialAuthView.as_view(), name='social_auth'),
    path('social-config/', SocialAuthConfigView.as_view(), name='social_auth_config'),

    # Registration and Email
    path('register/', RegisterView.as_view(), name='register'),
    path('check-email/', UserCheckEmailView.as_view(), name='check_email'),

    # Password Management
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetView.as_view(), name='password_reset_confirm'),

    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', ChangePasswordView.as_view(), name='change_password'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify_token'),

    # User Details
    path('user/<uuid:user_id>/', UserDetailView.as_view(), name='user_detail'),
]
