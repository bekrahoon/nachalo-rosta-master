from rest_framework import serializers

from .models import Listing, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега объявления"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ListingSerializer(serializers.ModelSerializer):
    """Публичный сериализатор объявления каталога (только для чтения)"""

    listing_type_display = serializers.CharField(source='get_listing_type_display', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'listing_type', 'listing_type_display',
            'organization_name', 'region', 'is_online',
            'start_date', 'end_date', 'application_deadline',
            'source_url', 'cover_image_url', 'tags', 'is_featured', 'created_at',
        ]
