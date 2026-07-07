from django.db.models import Count, DecimalField, Sum
from django.db.models.functions import Coalesce, TruncMonth
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ImpactRecord
from .serializers import ImpactRecordSerializer, ImpactSummarySerializer


class MyImpactRecordsView(generics.ListAPIView):
    """Записи воздействия текущего пользователя"""

    serializer_class = ImpactRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ImpactRecord.objects.filter(user=self.request.user).select_related('event')


class ImpactAnalyticsView(APIView):
    """
    Аналитика социального воздействия: суммарные показатели и
    помесячная динамика часов/средств для построения графиков.

    По умолчанию агрегирует данные по всем волонтёрам.
    Передайте ?mine=true, чтобы получить только свои данные.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = ImpactRecord.objects.all()
        if request.query_params.get('mine') == 'true':
            queryset = queryset.filter(user=request.user)

        totals = queryset.aggregate(
            total_hours=Coalesce(Sum('hours_contributed'), 0.0),
            total_funds=Coalesce(
                Sum('funds_raised_or_equivalent'),
                0,
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
            total_records=Count('id'),
            total_volunteers=Count('user', distinct=True),
        )

        monthly = (
            queryset
            .annotate(month=TruncMonth('recorded_at'))
            .values('month')
            .annotate(
                total_hours=Coalesce(Sum('hours_contributed'), 0.0),
                total_funds=Coalesce(
                    Sum('funds_raised_or_equivalent'),
                    0,
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
                volunteers_count=Count('user', distinct=True),
                records_count=Count('id'),
            )
            .order_by('month')
        )

        data = {
            'total_hours': totals['total_hours'],
            'total_funds': totals['total_funds'],
            'total_volunteers': totals['total_volunteers'],
            'total_records': totals['total_records'],
            'monthly': list(monthly),
        }

        serializer = ImpactSummarySerializer(data)
        return Response(serializer.data)
