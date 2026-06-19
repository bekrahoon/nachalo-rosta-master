from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Team, TeamMember
from .serializers import (
    TeamCreateUpdateSerializer,
    TeamDetailSerializer,
    TeamListSerializer,
)


class IsTeamLeaderOrReadOnly(permissions.BasePermission):
    """Только лидер команды может изменять/удалять команду"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action in ('join', 'leave'):
            return True
        return obj.leader == request.user


class TeamViewSet(viewsets.ModelViewSet):
    """CRUD для команд волонтёров"""

    queryset = Team.objects.select_related('leader', 'listing').prefetch_related('teammember_set__user')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTeamLeaderOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'requirements']

    def get_serializer_class(self):
        if self.action == 'list':
            return TeamListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return TeamCreateUpdateSerializer
        return TeamDetailSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Присоединиться к команде напрямую (без набора)"""
        team = self.get_object()

        if TeamMember.objects.filter(team=team, user=request.user).exists():
            return Response(
                {'detail': 'Вы уже состоите в этой команде'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if team.max_members and team.members.count() >= team.max_members:
            return Response(
                {'detail': 'В команде уже максимальное количество участников'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        TeamMember.objects.create(team=team, user=request.user, role='member')
        team.total_volunteers = team.members.count()
        team.save(update_fields=['total_volunteers'])

        return Response(
            {'message': 'Вы присоединились к команде'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Покинуть команду"""
        team = self.get_object()

        if team.leader == request.user:
            return Response(
                {'detail': 'Лидер не может покинуть команду'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = TeamMember.objects.filter(team=team, user=request.user).delete()
        if not deleted:
            return Response(
                {'detail': 'Вы не состоите в этой команде'},
                status=status.HTTP_404_NOT_FOUND,
            )

        team.total_volunteers = team.members.count()
        team.save(update_fields=['total_volunteers'])

        return Response({'message': 'Вы покинули команду'})
