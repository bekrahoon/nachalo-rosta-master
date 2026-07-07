from rest_framework import serializers

from .models import Badge, Level, Stats, UserBadge


class BadgeSerializer(serializers.ModelSerializer):
    """Сериализатор достижения/бейджа"""

    criteria_type_display = serializers.CharField(source='get_criteria_type_display', read_only=True)
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)

    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'icon', 'icon_url', 'condition',
            'criteria_type', 'criteria_type_display', 'criteria_value',
            'points', 'rarity', 'rarity_display', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UserBadgeSerializer(serializers.ModelSerializer):
    """Сериализатор полученного пользователем достижения"""

    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'unlocked_at']
        read_only_fields = ['id', 'unlocked_at']


class LevelSerializer(serializers.ModelSerializer):
    """Сериализатор уровня волонтёра"""

    class Meta:
        model = Level
        fields = ['id', 'name', 'icon', 'min_points', 'max_points', 'color']
        read_only_fields = ['id']


class StatsSerializer(serializers.ModelSerializer):
    """Сериализатор статистики пользователя"""

    level = LevelSerializer(read_only=True)
    badges_count = serializers.SerializerMethodField()

    class Meta:
        model = Stats
        fields = [
            'total_hours', 'total_events', 'total_teams', 'total_points',
            'level', 'best_month_hours', 'best_month', 'badges_count', 'updated_at',
        ]

    def get_badges_count(self, obj):
        return obj.user.badges.count()
