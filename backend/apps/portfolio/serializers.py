from rest_framework import serializers

from apps.aggregator.serializers import ListingSerializer
from .models import PortfolioProfile, SavedListing


class PortfolioProfileSerializer(serializers.ModelSerializer):
    """Настройки отображения портфолио (редактируемые пользователем)"""

    class Meta:
        model = PortfolioProfile
        fields = ['title', 'description', 'is_public', 'updated_at']
        read_only_fields = ['updated_at']


class SavedListingSerializer(serializers.ModelSerializer):
    """Сохранённая пользователем возможность"""

    listing = ListingSerializer(read_only=True)

    class Meta:
        model = SavedListing
        fields = ['id', 'listing', 'created_at']
        read_only_fields = fields


class PortfolioSerializer(serializers.Serializer):
    """Сводка портфолио волонтёра"""

    profile = PortfolioProfileSerializer()
    saved_listings = SavedListingSerializer(many=True)
