from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.aggregator.models import Listing
from .models import SavedListing
from .serializers import PortfolioSerializer, PortfolioProfileSerializer, SavedListingSerializer
from .services import build_portfolio_context, get_or_create_portfolio_profile


class PortfolioSummaryView(APIView):
    """JSON-сводка портфолио текущего пользователя"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        context = build_portfolio_context(request.user)
        serializer = PortfolioSerializer(context)
        return Response(serializer.data)


class PortfolioProfileView(APIView):
    """Просмотр и редактирование настроек отображения портфолио"""

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        profile = get_or_create_portfolio_profile(request.user)
        serializer = PortfolioProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SavedListingListView(APIView):
    """Список сохранённых пользователем возможностей и добавление новых"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved = (
            SavedListing.objects.filter(user=request.user)
            .select_related('listing')
            .prefetch_related('listing__tags')
            .order_by('-created_at')
        )
        serializer = SavedListingSerializer(saved, many=True)
        return Response(serializer.data)

    def post(self, request):
        listing = get_object_or_404(Listing, id=request.data.get('listing'))
        saved, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
        serializer = SavedListingSerializer(saved)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SavedListingDetailView(APIView):
    """Удаление возможности из сохранённых"""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, listing_id):
        SavedListing.objects.filter(user=request.user, listing_id=listing_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
