from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, EventVolunteer, EventRating, EventCategory, EventStatus

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Минимальная информация о пользователе"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar']


class EventVolunteerSerializer(serializers.ModelSerializer):
    """Сериализатор участия волонтёра в событии"""
    volunteer = UserMinimalSerializer(read_only=True)
    event = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = EventVolunteer
        fields = [
            'id', 'event', 'volunteer', 'status', 'hours_completed',
            'applied_at', 'joined_at', 'completed_at', 'rating', 'feedback'
        ]
        read_only_fields = ['id', 'applied_at']


class EventRatingSerializer(serializers.ModelSerializer):
    """Сериализатор оценки события"""
    volunteer = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = EventRating
        fields = ['id', 'event', 'volunteer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'volunteer']


class EventListSerializer(serializers.ModelSerializer):
    """Сериализатор списка событий (короткая версия)"""
    
    organizer = UserMinimalSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_volunteers = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'status', 'status_display', 'organizer', 'start_date', 'end_date',
            'location', 'latitude', 'longitude', 'max_volunteers', 'total_volunteers',
            'available_slots', 'is_online', 'is_featured', 'image', 'volunteer_hours',
            'distance_km', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_volunteers', 'available_slots', 'created_at'
        ]

    def get_distance_km(self, obj):
        """Расстояние до события в км (если аннотировано в queryset)"""
        distance = getattr(obj, 'distance', None)
        if distance is None:
            return None
        return round(distance, 2)


class EventDetailSerializer(serializers.ModelSerializer):
    """Сериализатор полной информации о событии"""
    
    organizer = UserMinimalSerializer(read_only=True)
    volunteers = EventVolunteerSerializer(
        source='eventvolunteer_set',
        many=True,
        read_only=True
    )
    ratings = EventRatingSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_volunteers = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    is_user_joined = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'status', 'status_display', 'organizer', 'start_date', 'end_date',
            'location', 'latitude', 'longitude', 'max_volunteers', 'total_volunteers',
            'available_slots', 'volunteers', 'required_skills', 'volunteer_hours',
            'contact_person', 'contact_phone', 'contact_email', 'image',
            'is_featured', 'is_online', 'ratings', 'average_rating',
            'is_user_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_volunteers', 'available_slots', 'volunteers',
            'ratings', 'average_rating', 'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        """Средний рейтинг события"""
        ratings = obj.ratings.all()
        if not ratings:
            return None
        total = sum(r.rating for r in ratings)
        return round(total / len(ratings), 1)
    
    def get_is_user_joined(self, obj):
        """Присоединился ли текущий пользователь"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.eventvolunteer_set.filter(volunteer=request.user).exists()


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления события"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'status',
            'start_date', 'end_date', 'location', 'latitude', 'longitude',
            'max_volunteers', 'required_skills', 'volunteer_hours',
            'contact_person', 'contact_phone', 'contact_email', 'image',
            'is_featured', 'is_online'
        ]
    
    def validate(self, data):
        """Валидация дат"""
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                'Дата начала должна быть раньше даты окончания'
            )
        return data
    
    def create(self, validated_data):
        """Создание события"""
        request = self.context.get('request')
        validated_data['organizer'] = request.user
        return super().create(validated_data)


class EventJoinSerializer(serializers.Serializer):
    """Сериализатор для присоединения волонтёра к событию"""
    
    event_id = serializers.UUIDField()
    
    def validate_event_id(self, value):
        """Проверка что событие существует"""
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError('Событие не найдено')
        
        if event.is_full:
            raise serializers.ValidationError('Максимум волонтёров достигнуто')
        
        request = self.context.get('request')
        if EventVolunteer.objects.filter(
            event=event,
            volunteer=request.user
        ).exists():
            raise serializers.ValidationError('Вы уже присоединились к этому событию')
        
        return value


class EventLeaveSerializer(serializers.Serializer):
    """Сериализатор для отмены участия волонтёра"""
    
    event_id = serializers.UUIDField()


class EventStatsSerializer(serializers.Serializer):
    """Статистика по событиям"""
    total_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    completed_events = serializers.IntegerField()
    total_volunteers = serializers.IntegerField()
    total_hours = serializers.FloatField()
