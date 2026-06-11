from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.achievements.services import update_stats_on_team_join
from .models import RecruitmentSlot, Team, TeamApplication, TeamApplicationStatus, TeamMember
from .serializers import (
    RecruitmentSlotCreateSerializer,
    RecruitmentSlotSerializer,
    TeamApplicationApproveSerializer,
    TeamApplicationCreateSerializer,
    TeamApplicationSerializer,
    TeamCreateUpdateSerializer,
    TeamDetailSerializer,
    TeamListSerializer,
)


class IsTeamLeaderOrReadOnly(permissions.BasePermission):
    """Только лидер команды может изменять/удалять команду"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.leader == request.user


class TeamViewSet(viewsets.ModelViewSet):
    """CRUD для команд волонтёров"""

    queryset = Team.objects.select_related('leader').prefetch_related('teammember_set__user')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTeamLeaderOrReadOnly]

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

        TeamMember.objects.create(team=team, user=request.user, role='member')
        team.total_volunteers = team.members.count()
        team.save(update_fields=['total_volunteers'])

        update_stats_on_team_join(request.user)

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


class RecruitmentSlotViewSet(viewsets.ModelViewSet):
    """Наборы волонтёров команды на события"""

    queryset = RecruitmentSlot.objects.select_related('team', 'event', 'team__leader')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecruitmentSlotCreateSerializer
        return RecruitmentSlotSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_update(self, serializer):
        slot = self.get_object()
        if slot.team.leader != self.request.user:
            raise permissions.PermissionDenied('Только лидер команды может изменять набор')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.team.leader != self.request.user:
            raise permissions.PermissionDenied('Только лидер команды может удалять набор')
        instance.delete()

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Подать заявку на участие в наборе"""
        slot = self.get_object()

        serializer = TeamApplicationCreateSerializer(
            data={'slot': slot.id, 'message': request.data.get('message', '')},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        return Response(
            TeamApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Список заявок на набор (только для лидера команды)"""
        slot = self.get_object()

        if slot.team.leader != request.user:
            return Response(
                {'detail': 'Только лидер команды может просматривать заявки'},
                status=status.HTTP_403_FORBIDDEN,
            )

        applications = slot.applications.select_related('applicant')
        serializer = TeamApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class TeamApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    """Заявки текущего пользователя"""

    serializer_class = TeamApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TeamApplication.objects.filter(
            applicant=self.request.user
        ).select_related('slot', 'slot__team', 'slot__event')

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Одобрить или отклонить заявку (только лидер команды набора)"""
        application = TeamApplication.objects.select_related(
            'slot', 'slot__team'
        ).get(pk=pk)

        if application.slot.team.leader != request.user:
            return Response(
                {'detail': 'Только лидер команды может рассматривать заявки'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TeamApplicationApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        if application.status != TeamApplicationStatus.PENDING:
            return Response(
                {'detail': 'Заявка уже рассмотрена'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status == TeamApplicationStatus.APPROVED and application.slot.remaining_slots <= 0:
            return Response(
                {'detail': 'Свободных мест больше нет'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = new_status
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])

        if new_status == TeamApplicationStatus.APPROVED:
            team = application.slot.team
            TeamMember.objects.get_or_create(
                team=team, user=application.applicant, defaults={'role': 'member'}
            )
            team.total_volunteers = team.members.count()
            team.save(update_fields=['total_volunteers'])
            update_stats_on_team_join(application.applicant)

        return Response(TeamApplicationSerializer(application).data)
