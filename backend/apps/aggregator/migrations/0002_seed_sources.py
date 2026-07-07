from django.db import migrations

# Стартовый набор источников для MVP сбора объявлений.
# Telegram-источники используют публичный веб-просмотр t.me/s/<identifier> —
# не требует авторизации (см. fetch_method в config).
SOURCES_SEED = [
    # --- Telegram ---
    dict(
        name='Росмолодёжь.Добро',
        source_type='telegram',
        identifier='dobroinrussia',
        url='https://t.me/s/dobroinrussia',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Официальный канал федерального проекта «Росмолодёжь.Добро» — '
              'анонсы волонтёрских акций и новости.',
    ),
    dict(
        name='Добро.рф',
        source_type='telegram',
        identifier='d_o_b_r_o_r_u',
        url='https://t.me/s/d_o_b_r_o_r_u',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Крупнейшая платформа волонтёрства в России — новости и '
              'анонсы мероприятий.',
    ),
    dict(
        name='Мосволонтёр',
        source_type='telegram',
        identifier='mosvol',
        url='https://t.me/s/mosvol',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Волонтёрский центр Москвы — городские волонтёрские проекты.',
    ),
    dict(
        name='Хакатоны | Hackathon list',
        source_type='telegram',
        identifier='Hackathonlist',
        url='https://t.me/s/Hackathonlist',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Крупный анонс-канал хакатонов и IT-соревнований (~15K подписчиков).',
    ),
    dict(
        name='Все конкурсы, гранты, стипендии',
        source_type='telegram',
        identifier='vsekonkursy',
        url='https://t.me/s/vsekonkursy',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Конкурсы, гранты, стипендии и вакансии для школьников и студентов.',
    ),
    dict(
        name='Росмолодёжь.Гранты',
        source_type='telegram',
        identifier='rosmolodezgrants',
        url='https://t.me/s/rosmolodezgrants',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Официальный канал конкурса грантов Росмолодёжи и молодёжных форумов.',
    ),
    dict(
        name='Grants.kz',
        source_type='telegram',
        identifier='grants_scholarships',
        url='https://t.me/s/grants_scholarships',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Гранты и стипендии для молодёжи СНГ/Казахстана.',
    ),

    # --- Сайты ---
    dict(
        name='Timepad API',
        source_type='website',
        identifier='https://api.timepad.ru/v1/events',
        url='https://dev.timepad.ru/',
        trust_level='quarantine',
        config={
            'fetch_method': 'timepad_api',
            'requires_token': True,
            'rate_limit': '60/min',
            'docs': 'https://dev.timepad.ru/api/swagger-doc/',
        },
        notes='Официальный REST API Timepad — события по категориям и городам. '
              'Требуется API-токен (см. dev.timepad.ru).',
    ),
    dict(
        name='Volunteer.kg — проекты',
        source_type='website',
        identifier='https://volunteer.kg/en/project/',
        url='https://volunteer.kg/en/project/',
        config={'fetch_method': 'html_scrape'},
        notes='Портал волонтёрских проектов Кыргызстана.',
    ),
    dict(
        name='Hackathons.pro',
        source_type='website',
        identifier='https://hackathons.pro/',
        url='https://hackathons.pro/',
        config={'fetch_method': 'html_scrape'},
        notes='Агрегатор хакатонов и IT-олимпиад. Перед сбором проверить robots.txt.',
    ),
    dict(
        name='Всехакатоны.рф',
        source_type='website',
        identifier='https://xn--80aa3anexr8c.xn--p1ai/',
        url='https://xn--80aa3anexr8c.xn--p1ai/',
        config={'fetch_method': 'html_scrape'},
        notes='Агрегатор хакатонов России (всехакатоны.рф). '
              'Перед сбором проверить robots.txt.',
    ),
    dict(
        name='Добро.рф (сайт)',
        source_type='website',
        identifier='https://dobro.ru/',
        url='https://dobro.ru/',
        is_active=False,
        config={'fetch_method': 'tbd'},
        notes='Крупнейшая база вакансий волонтёрства в РФ. Публичного API не найдено — '
              'требуется либо договориться о партнёрской интеграции, либо аккуратный '
              'scraping с проверкой robots.txt. Источник выключен до решения.',
    ),

    # --- VK (screen_name требует проверки перед активацией) ---
    dict(
        name='Росмолодёжь (VK)',
        source_type='vk',
        identifier='rosmolodez',
        is_active=False,
        config={'fetch_method': 'vk_wall_get'},
        notes='Проверьте актуальный screen_name паблика в VK перед активацией.',
    ),
    dict(
        name='Российские студенческие отряды (VK)',
        source_type='vk',
        identifier='studotryad',
        is_active=False,
        config={'fetch_method': 'vk_wall_get'},
        notes='Проверьте актуальный screen_name паблика в VK перед активацией.',
    ),
    dict(
        name='Волонтёры-медики (VK)',
        source_type='vk',
        identifier='volonter_medik',
        is_active=False,
        config={'fetch_method': 'vk_wall_get'},
        notes='Проверьте актуальный screen_name паблика в VK перед активацией.',
    ),
    dict(
        name='Большая перемена (VK)',
        source_type='vk',
        identifier='bolshayaperemena',
        is_active=False,
        config={'fetch_method': 'vk_wall_get'},
        notes='Проверьте актуальный screen_name паблика в VK перед активацией.',
    ),
]


def seed_sources(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')
    for entry in SOURCES_SEED:
        entry = dict(entry)
        source_type = entry.pop('source_type')
        identifier = entry.pop('identifier')
        Source.objects.update_or_create(
            source_type=source_type,
            identifier=identifier,
            defaults=entry,
        )


def remove_sources(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')
    for entry in SOURCES_SEED:
        Source.objects.filter(
            source_type=entry['source_type'],
            identifier=entry['identifier'],
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_sources, remove_sources),
    ]
