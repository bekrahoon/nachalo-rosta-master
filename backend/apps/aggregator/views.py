from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Listing, ListingStatus, ListingType
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ReadOnlyModelViewSet):
    """Публичный каталог объявлений (волонтёрство, хакатоны, гранты и т.п.)"""

    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = {
        'listing_type': ['exact'],
        'region': ['exact'],
        'is_online': ['exact'],
        'tags__slug': ['exact'],
    }
    search_fields = ['title', 'description', 'organization_name']
    ordering_fields = ['created_at', 'start_date', 'application_deadline']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Listing.objects.filter(status=ListingStatus.PUBLISHED)
            .select_related('raw_item__source')
            .prefetch_related('tags')
        )

    @action(detail=False, methods=['get'])
    def new_count(self, request):
        since = request.query_params.get('since')
        if since:
            try:
                cutoff = timezone.datetime.fromisoformat(since)
            except ValueError:
                cutoff = timezone.now() - timedelta(days=1)
        else:
            cutoff = timezone.now() - timedelta(days=1)
        count = self.get_queryset().filter(created_at__gt=cutoff).count()
        return Response({'count': count, 'since': cutoff.isoformat()})

    @action(detail=False, methods=['get'])
    def facets(self, request):
        """Доступные значения для фильтров каталога (типы, регионы, теги)"""
        queryset = self.get_queryset()

        regions = (
            queryset.exclude(region='')
            .order_by('region')
            .values_list('region', flat=True)
            .distinct()
        )
        tags = (
            queryset.values('tags__slug', 'tags__name')
            .exclude(tags__isnull=True)
            .order_by('tags__name')
            .distinct()
        )

        return Response({
            'listing_types': [
                {'value': value, 'label': label}
                for value, label in ListingType.choices
            ],
            'regions': list(regions),
            'tags': [
                {'slug': item['tags__slug'], 'name': item['tags__name']}
                for item in tags
            ],
        })
