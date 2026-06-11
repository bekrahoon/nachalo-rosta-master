from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response

from .models import Badge, Level, UserBadge
from .serializers import BadgeSerializer, LevelSerializer, StatsSerializer, UserBadgeSerializer
from .services import get_or_create_stats


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """Список всех доступных достижений"""

    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """Список уровней волонтёра"""

    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.AllowAny]


class MyBadgesView(generics.ListAPIView):
    """Достижения текущего пользователя"""

    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge')


class MyStatsView(generics.RetrieveAPIView):
    """Статистика текущего пользователя"""

    serializer_class = StatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_stats(self.request.user)
