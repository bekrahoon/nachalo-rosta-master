from rest_framework import serializers

from apps.events.serializers import EventListSerializer
from .models import EventRecommendation


class EventRecommendationSerializer(serializers.ModelSerializer):
    """Сериализатор рекомендации события"""

    event = EventListSerializer(read_only=True)

    class Meta:
        model = EventRecommendation
        fields = ['id', 'event', 'match_score', 'reason', 'created_at']
        read_only_fields = fields
