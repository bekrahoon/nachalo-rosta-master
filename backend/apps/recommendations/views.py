from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EventRecommendation
from .serializers import EventRecommendationSerializer
from .tasks import generate_recommendations


class MyRecommendationsView(generics.ListAPIView):
    """Список AI-рекомендаций событий для текущего пользователя"""

    serializer_class = EventRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            EventRecommendation.objects.filter(user=self.request.user)
            .select_related('listing', 'listing__raw_item__source')
            .prefetch_related('listing__tags')
        )


class RefreshRecommendationsView(APIView):
    """Запустить фоновую генерацию свежих рекомендаций для текущего пользователя"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        generate_recommendations.delay(str(request.user.id))
        return Response(
            {'message': 'Генерация рекомендаций запущена. Загляните на эту страницу позже.'},
            status=status.HTTP_202_ACCEPTED,
        )
