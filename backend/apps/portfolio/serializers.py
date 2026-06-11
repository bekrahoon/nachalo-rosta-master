from rest_framework import serializers

from apps.achievements.serializers import BadgeSerializer, StatsSerializer
from apps.events.serializers import EventListSerializer


class PortfolioSerializer(serializers.Serializer):
    """Сводка портфолио волонтёра"""

    stats = StatsSerializer()
    total_hours = serializers.FloatField()
    completed_events = EventListSerializer(many=True)
    badges = BadgeSerializer(many=True)
