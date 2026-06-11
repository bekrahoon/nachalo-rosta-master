from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Avg, F, FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Sin, Radians, Least, Greatest

from .models import Event, EventVolunteer, EventRating
from .serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateUpdateSerializer,
    EventVolunteerSerializer,
    EventRatingSerializer,
    EventJoinSerializer,
    EventLeaveSerializer,
)
from apps.accounts.permissions import IsOrganizerOrAdmin


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet для управления событиями"""
    
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_online']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        """Возвращает нужный сериализатор в зависимости от action"""
        if self.action == 'retrieve':
            return EventDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer
    
    def get_queryset(self):
        """Фильтрация событий"""
        queryset = super().get_queryset()

        # Фильтр по дате
        date_filter = self.request.query_params.get('date_from')
        if date_filter:
            from datetime import datetime
            try:
                date = datetime.fromisoformat(date_filter)
                queryset = queryset.filter(start_date__gte=date)
            except ValueError:
                pass
        
        # Фильтр "мои события"
        if self.request.query_params.get('my_events') == 'true':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    Q(organizer=self.request.user) |
                    Q(eventvolunteer__volunteer=self.request.user)
                )
        
        return queryset.distinct()
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Получить предстоящие события"""
        events = self.get_queryset().filter(
            start_date__gte=timezone.now(),
            status__in=['upcoming', 'draft']
        )[:10]
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Получить события рядом с указанной точкой.
        Параметры запроса: lat, lng (координаты точки) и radius_km (радиус поиска, по умолчанию 10 км).
        Использует формулу гаверсинуса (Haversine) для расчёта расстояния.
        """
        lat_param = request.query_params.get('lat')
        lng_param = request.query_params.get('lng')
        radius_param = request.query_params.get('radius_km', '10')

        if lat_param is None or lng_param is None:
            return Response(
                {'detail': 'Параметры lat и lng обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(lat_param)
            lng = float(lng_param)
            radius_km = float(radius_param)
        except ValueError:
            return Response(
                {'detail': 'lat, lng и radius_km должны быть числами'},
                status=status.HTTP_400_BAD_REQUEST
            )

        EARTH_RADIUS_KM = 6371.0

        queryset = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False,
        )

        # Аргумент ACos из-за погрешности округления может выйти за пределы [-1, 1]
        central_angle_cos = Greatest(
            Least(
                ExpressionWrapper(
                    Sin(Radians(lat)) * Sin(Radians(F('latitude'))) +
                    Cos(Radians(lat)) * Cos(Radians(F('latitude'))) *
                    Cos(Radians(F('longitude')) - Radians(lng)),
                    output_field=FloatField()
                ),
                1.0
            ),
            -1.0
        )

        queryset = queryset.annotate(
            distance=ExpressionWrapper(
                ACos(central_angle_cos) * EARTH_RADIUS_KM,
                output_field=FloatField()
            )
        ).filter(distance__lte=radius_km).order_by('distance')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = EventListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Получить рекомендуемые события"""
        events = self.get_queryset().filter(
            is_featured=True,
            start_date__gte=timezone.now()
        )[:6]
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Присоединиться к событию"""
        event = self.get_object()
        
        serializer = EventJoinSerializer(
            data={'event_id': event.id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Создаём участие
            volunteer_record = EventVolunteer.objects.create(
                event=event,
                volunteer=request.user,
                status='approved'
            )
            
            return Response(
                {
                    'message': 'Вы присоединились к событию',
                    'volunteer': EventVolunteerSerializer(volunteer_record).data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Покинуть событие"""
        event = self.get_object()
        
        try:
            volunteer_record = EventVolunteer.objects.get(
                event=event,
                volunteer=request.user
            )
            volunteer_record.delete()
            
            return Response(
                {'message': 'Вы покинули событие'},
                status=status.HTTP_200_OK
            )
        except EventVolunteer.DoesNotExist:
            return Response(
                {'detail': 'Вы не участвуете в этом событии'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def volunteers(self, request, pk=None):
        """Получить всех волонтёров события"""
        event = self.get_object()
        volunteers = event.eventvolunteer_set.all()
        
        serializer = EventVolunteerSerializer(volunteers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOrganizerOrAdmin])
    def approve_volunteer(self, request, pk=None):
        """Одобрить волонтёра (только организатор)"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {'detail': 'Только организатор может управлять волонтёрами'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        volunteer_id = request.data.get('volunteer_id')
        
        try:
            volunteer_record = EventVolunteer.objects.get(
                id=volunteer_id,
                event=event
            )
            volunteer_record.status = 'approved'
            volunteer_record.save()
            
            return Response(
                {
                    'message': 'Волонтёр одобрен',
                    'volunteer': EventVolunteerSerializer(volunteer_record).data
                }
            )
        except EventVolunteer.DoesNotExist:
            return Response(
                {'detail': 'Волонтёр не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsOrganizerOrAdmin])
    def mark_completed(self, request, pk=None):
        """Отметить волонтёра как завершившего событие"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {'detail': 'Только организатор может управлять волонтёрами'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        volunteer_id = request.data.get('volunteer_id')
        
        try:
            volunteer_record = EventVolunteer.objects.get(
                id=volunteer_id,
                event=event
            )
            volunteer_record.status = 'completed'
            volunteer_record.hours_completed = event.volunteer_hours
            volunteer_record.completed_at = timezone.now()
            volunteer_record.save()
            
            return Response(
                {
                    'message': 'Волонтёр отмечен как завершивший событие',
                    'volunteer': EventVolunteerSerializer(volunteer_record).data
                }
            )
        except EventVolunteer.DoesNotExist:
            return Response(
                {'detail': 'Волонтёр не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Оценить событие"""
        event = self.get_object()
        
        # Проверяем что пользователь участвовал в событии
        if not EventVolunteer.objects.filter(
            event=event,
            volunteer=request.user
        ).exists():
            return Response(
                {'detail': 'Вы не участвовали в этом событии'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Удаляем старую оценку если есть
        EventRating.objects.filter(
            event=event,
            volunteer=request.user
        ).delete()
        
        # Создаём новую оценку
        serializer = EventRatingSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            rating = serializer.save(
                event=event,
                volunteer=request.user
            )
            return Response(
                EventRatingSerializer(rating).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        """Создание события (только для организаторов)"""
        if not request.user.is_organizer:
            return Response(
                {'detail': 'Только организаторы могут создавать события'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Обновление события (только организатор)"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {'detail': 'Только организатор может обновлять событие'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Удаление события (только организатор)"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {'detail': 'Только организатор может удалять событие'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
