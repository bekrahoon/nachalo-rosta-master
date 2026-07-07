from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Team,
    TeamMember,
)

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar']


class TeamListingSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    listing_type = serializers.CharField()
    listing_type_display = serializers.CharField(source='get_listing_type_display')
    source_url = serializers.URLField()
    region = serializers.CharField()


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role', 'role_display', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class TeamListSerializer(serializers.ModelSerializer):
    leader = UserMinimalSerializer(read_only=True)
    listing = TeamListingSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'requirements', 'max_members',
            'leader', 'listing', 'status', 'status_display',
            'avatar', 'total_hours', 'total_volunteers', 'members_count',
            'is_member', 'is_leader', 'created_at',
        ]
        read_only_fields = fields

    def get_members_count(self, obj):
        return obj.members.count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

    def get_is_leader(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.leader_id == request.user.id
        return False


class TeamDetailSerializer(serializers.ModelSerializer):
    leader = UserMinimalSerializer(read_only=True)
    listing = TeamListingSerializer(read_only=True)
    members = TeamMemberSerializer(source='teammember_set', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'requirements', 'max_members',
            'leader', 'listing', 'members', 'status', 'status_display',
            'avatar', 'total_hours', 'total_volunteers', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'leader', 'listing', 'members', 'total_hours', 'total_volunteers',
            'created_at', 'updated_at',
        ]


class TeamCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'requirements', 'max_members', 'listing', 'status', 'avatar']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['leader'] = request.user
        team = super().create(validated_data)
        TeamMember.objects.create(team=team, user=request.user, role='leader')
        return team


