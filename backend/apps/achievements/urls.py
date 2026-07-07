from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BadgeViewSet, LevelViewSet, MyBadgesView, MyStatsView

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'levels', LevelViewSet, basename='level')

app_name = 'achievements'

urlpatterns = [
    path('my-badges/', MyBadgesView.as_view(), name='my_badges'),
    path('my-stats/', MyStatsView.as_view(), name='my_stats'),
    path('', include(router.urls)),
]
