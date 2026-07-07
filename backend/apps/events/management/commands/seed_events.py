from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.events.models import Event, EventCategory, EventStatus

User = get_user_model()

SAMPLE_EVENTS = [
    {
        'title': 'Очистка парка «Ала-Арча»',
        'description': (
            'Присоединяйтесь к команде волонтёров для уборки мусора и посадки '
            'деревьев в парке Ала-Арча. Перчатки и мешки для мусора предоставляются.'
        ),
        'category': EventCategory.ENVIRONMENT,
        'location': 'Бишкек, парк Ала-Арча',
        'days_ahead': 7,
        'duration_hours': 4,
        'max_volunteers': 20,
        'volunteer_hours': 4,
        'required_skills': 'физическая активность, работа в команде',
        'is_online': False,
    },
    {
        'title': 'Уроки программирования для школьников',
        'description': (
            'Помогите провести вводные занятия по программированию на Scratch и '
            'Python для учеников 5-9 классов. Опыт преподавания не обязателен.'
        ),
        'category': EventCategory.EDUCATION,
        'location': 'Онлайн',
        'days_ahead': 10,
        'duration_hours': 2,
        'max_volunteers': 8,
        'volunteer_hours': 2,
        'required_skills': 'программирование, Python, коммуникация',
        'is_online': True,
    },
    {
        'title': 'Посещение дома престарелых',
        'description': (
            'Проведите время с пожилыми людьми: общение, чтение книг, помощь с '
            'мелкими бытовыми задачами и организация настольных игр.'
        ),
        'category': EventCategory.SOCIAL,
        'location': 'Токмок, ул. Ленина 12',
        'days_ahead': 5,
        'duration_hours': 3,
        'max_volunteers': 15,
        'volunteer_hours': 3,
        'required_skills': 'эмпатия, общение',
        'is_online': False,
    },
    {
        'title': 'Донорская акция «Поделись жизнью»',
        'description': (
            'Помогите организовать донорскую акцию: регистрация участников, '
            'информирование о процедуре, поддержка доноров после сдачи крови.'
        ),
        'category': EventCategory.HEALTH,
        'location': 'Бишкек, Республиканский центр крови',
        'days_ahead': 14,
        'duration_hours': 5,
        'max_volunteers': 12,
        'volunteer_hours': 5,
        'required_skills': 'организация, работа с людьми',
        'is_online': False,
    },
    {
        'title': 'Городской фестиваль уличного искусства',
        'description': (
            'Волонтёры нужны для помощи в организации фестиваля: установка '
            'инсталляций, навигация посетителей, помощь художникам.'
        ),
        'category': EventCategory.CULTURE,
        'location': 'Бишкек, ЦУМ площадь',
        'days_ahead': 21,
        'duration_hours': 6,
        'max_volunteers': 25,
        'volunteer_hours': 6,
        'required_skills': 'творчество, организация',
        'is_online': False,
    },
    {
        'title': 'Благотворительный забег «Беги ради добра»',
        'description': (
            'Помогите с организацией благотворительного забега: регистрация '
            'участников, разметка трассы, раздача воды на дистанции.'
        ),
        'category': EventCategory.SPORTS,
        'location': 'Бишкек, набережная Аламедин',
        'days_ahead': 18,
        'duration_hours': 4,
        'max_volunteers': 30,
        'volunteer_hours': 4,
        'required_skills': 'спорт, организация',
        'is_online': False,
    },
    {
        'title': 'Онлайн-марафон по сбору средств для приюта животных',
        'description': (
            'Помогите провести онлайн-стрим в поддержку приюта для животных: '
            'модерация чата, продвижение в соцсетях, сбор пожертвований.'
        ),
        'category': EventCategory.SOCIAL,
        'location': 'Онлайн',
        'days_ahead': 9,
        'duration_hours': 3,
        'max_volunteers': 10,
        'volunteer_hours': 3,
        'required_skills': 'SMM, коммуникация',
        'is_online': True,
    },
    {
        'title': 'Эко-урок для младших классов',
        'description': (
            'Проведите интерактивный урок об экологии и переработке отходов для '
            'учеников начальной школы.'
        ),
        'category': EventCategory.EDUCATION,
        'location': 'Бишкек, школа №5',
        'days_ahead': 12,
        'duration_hours': 2,
        'max_volunteers': 6,
        'volunteer_hours': 2,
        'required_skills': 'педагогика, экология',
        'is_online': False,
    },
]


class Command(BaseCommand):
    help = 'Создаёт тестового организатора и набор реальных волонтёрских событий'

    def handle(self, *args, **options):
        organizer, created = User.objects.get_or_create(
            email='organizer@nachalo-rosta.local',
            defaults={
                'username': 'nachalo_organizer',
                'first_name': 'Начало',
                'last_name': 'Роста',
                'role': 'organizer',
                'is_active': True,
            },
        )
        if created:
            organizer.set_unusable_password()
            organizer.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Создан организатор: {organizer.email}'))
        elif organizer.role != 'organizer':
            organizer.role = 'organizer'
            organizer.save(update_fields=['role'])

        created_count = 0
        for data in SAMPLE_EVENTS:
            if Event.objects.filter(title=data['title']).exists():
                continue

            start_date = timezone.now() + timedelta(days=data['days_ahead'])
            end_date = start_date + timedelta(hours=data['duration_hours'])

            Event.objects.create(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                status=EventStatus.UPCOMING,
                organizer=organizer,
                start_date=start_date,
                end_date=end_date,
                location=data['location'],
                max_volunteers=data['max_volunteers'],
                required_skills=data['required_skills'],
                volunteer_hours=data['volunteer_hours'],
                is_online=data['is_online'],
                contact_email=organizer.email,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Создано событий: {created_count}'))
