from django.db import migrations

# Каналы с хакатонами, конкурсами и грантами для расширения охвата агрегатора.
SOURCES_SEED = [
    dict(
        name='Hackathon List',
        source_type='telegram',
        identifier='hackathons',
        url='https://t.me/s/hackathons',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Анонсы хакатонов в России и мире.',
    ),
    dict(
        name='Russian Hackers',
        source_type='telegram',
        identifier='RussianHackers_Channel',
        url='https://t.me/s/RussianHackers_Channel',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Хакатоны и IT-соревнования для разработчиков.',
    ),
    dict(
        name='Все конкурсы, гранты, стипендии',
        source_type='telegram',
        identifier='vsekonkursy',
        url='https://t.me/s/vsekonkursy',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Конкурсы, гранты, стипендии и вакансии для молодёжи.',
    ),
    dict(
        name='Grants.kz',
        source_type='telegram',
        identifier='grants_scholarships',
        url='https://t.me/s/grants_scholarships',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Гранты, стипендии и образовательные возможности для студентов СНГ.',
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
        ('aggregator', '0005_more_telegram_sources'),
    ]

    operations = [
        migrations.RunPython(seed_sources, remove_sources),
    ]
