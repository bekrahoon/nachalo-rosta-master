from rest_framework import serializers

from .models import ImpactRecord


class ImpactRecordSerializer(serializers.ModelSerializer):
    """Сериализатор записи социального воздействия"""

    event_title = serializers.CharField(source='event.title', read_only=True, default=None)

    class Meta:
        model = ImpactRecord
        fields = [
            'id', 'event', 'event_title', 'hours_contributed',
            'funds_raised_or_equivalent', 'recorded_at',
        ]
        read_only_fields = fields


class MonthlyImpactSerializer(serializers.Serializer):
    """Агрегированные данные воздействия по месяцам"""

    month = serializers.DateTimeField()
    total_hours = serializers.FloatField()
    total_funds = serializers.DecimalField(max_digits=14, decimal_places=2)
    volunteers_count = serializers.IntegerField()
    records_count = serializers.IntegerField()


class ImpactSummarySerializer(serializers.Serializer):
    """Общая сводка воздействия"""

    total_hours = serializers.FloatField()
    total_funds = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_volunteers = serializers.IntegerField()
    total_records = serializers.IntegerField()
    monthly = MonthlyImpactSerializer(many=True)
