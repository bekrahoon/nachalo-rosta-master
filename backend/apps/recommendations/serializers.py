from rest_framework import serializers

from apps.aggregator.serializers import ListingSerializer
from .models import EventRecommendation


class EventRecommendationSerializer(serializers.ModelSerializer):
    """Сериализатор рекомендации объявления"""

    listing = ListingSerializer(read_only=True)

    class Meta:
        model = EventRecommendation
        fields = ['id', 'listing', 'match_score', 'reason', 'created_at']
        read_only_fields = fields
