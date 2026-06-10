"""
URL configuration for Nachalo Rosta project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Apps
    path('api/v1/auth/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/events/', include('apps.events.urls', namespace='events')),
    path('api/v1/recommendations/', include('apps.recommendations.urls', namespace='recommendations')),
    path('api/v1/achievements/', include('apps.achievements.urls', namespace='achievements')),
    path('api/v1/portfolio/', include('apps.portfolio.urls', namespace='portfolio')),
    path('api/v1/teams/', include('apps.teams.urls', namespace='teams')),
    path('api/v1/impact/', include('apps.impact.urls', namespace='impact')),
    
    # Allauth (для социальной аутентификации и всяческих фич)
    path('accounts/', include('allauth.urls')),
]

# Static and Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns += [
            path('__debug__/', include('debug_toolbar.urls')),
        ]
