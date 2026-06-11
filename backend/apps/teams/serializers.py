from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.events.serializers import UserMinimalSerializer, EventListSerializer
from .models import (
    RecruitmentSlot,
    Team,
    TeamApplication,
    TeamApplicationStatus,
    TeamMember,
)

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Сериализатор члена команды"""

    user = UserMinimalSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role', 'role_display', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class TeamListSerializer(serializers.ModelSerializer):
    """Сериализатор списка команд (короткая версия)"""

    leader = UserMinimalSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'leader', 'status', 'status_display',
            'avatar', 'total_hours', 'total_volunteers', 'members_count', 'created_at',
        ]
        read_only_fields = fields

    def get_members_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(serializers.ModelSerializer):
    """Сериализатор полной информации о команде"""

    leader = UserMinimalSerializer(read_only=True)
    members = TeamMemberSerializer(source='teammember_set', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'leader', 'members', 'status', 'status_display',
            'avatar', 'total_hours', 'total_volunteers', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'leader', 'members', 'total_hours', 'total_volunteers',
            'created_at', 'updated_at',
        ]


class TeamCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления команды"""

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'status', 'avatar']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['leader'] = request.user
        team = super().create(validated_data)
        TeamMember.objects.create(team=team, user=request.user, role='leader')
        return team


class RecruitmentSlotSerializer(serializers.ModelSerializer):
    """Сериализатор набора волонтёров"""

    team = TeamListSerializer(read_only=True)
    event = EventListSerializer(read_only=True)
    remaining_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecruitmentSlot
        fields = [
            'id', 'team', 'event', 'description', 'slots_available',
            'remaining_slots', 'is_open', 'created_at',
        ]
        read_only_fields = ['id', 'team', 'event', 'remaining_slots', 'created_at']


class RecruitmentSlotCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания набора волонтёров (только для лидера команды)"""

    class Meta:
        model = RecruitmentSlot
        fields = ['id', 'team', 'event', 'description', 'slots_available', 'is_open']
        read_only_fields = ['id']

    def validate_team(self, team):
        request = self.context.get('request')
        if team.leader != request.user:
            raise serializers.ValidationError('Только лидер команды может создавать наборы')
        return team


class TeamApplicationSerializer(serializers.ModelSerializer):
    """Сериализатор заявки на участие в наборе"""

    applicant = UserMinimalSerializer(read_only=True)
    slot = RecruitmentSlotSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TeamApplication
        fields = [
            'id', 'slot', 'applicant', 'status', 'status_display',
            'message', 'applied_at', 'reviewed_at',
        ]
        read_only_fields = ['id', 'slot', 'applicant', 'status', 'applied_at', 'reviewed_at']


class TeamApplicationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор подачи заявки на участие в наборе"""

    class Meta:
        model = TeamApplication
        fields = ['id', 'slot', 'message']
        read_only_fields = ['id']

    def validate_slot(self, slot):
        if not slot.is_open:
            raise serializers.ValidationError('Набор закрыт')
        if slot.remaining_slots <= 0:
            raise serializers.ValidationError('Свободных мест больше нет')

        request = self.context.get('request')
        if TeamApplication.objects.filter(slot=slot, applicant=request.user).exists():
            raise serializers.ValidationError('Вы уже подали заявку на этот набор')

        return slot

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['applicant'] = request.user
        return super().create(validated_data)


class TeamApplicationApproveSerializer(serializers.Serializer):
    """Сериализатор одобрения/отклонения заявки лидером"""

    status = serializers.ChoiceField(
        choices=[TeamApplicationStatus.APPROVED, TeamApplicationStatus.REJECTED]
    )
