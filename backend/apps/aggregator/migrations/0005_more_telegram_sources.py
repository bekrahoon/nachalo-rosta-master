from django.db import migrations

# Дополнительные Telegram-каналы для расширения охвата агрегатора:
# гранты, стажировки, IT-события, хакатоны для молодёжи СНГ/Кыргызстана.
SOURCES_SEED = [
    dict(
        name='Talented Young',
        source_type='telegram',
        identifier='talentedyoung',
        url='https://t.me/s/talentedyoung',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Конкурсы, олимпиады и возможности для талантливой молодёжи.',
    ),
    dict(
        name='EduGrant KG',
        source_type='telegram',
        identifier='edugrant_kg',
        url='https://t.me/s/edugrant_kg',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Образовательные гранты и стипендии для жителей Кыргызстана.',
    ),
    dict(
        name='Grantium',
        source_type='telegram',
        identifier='grantium',
        url='https://t.me/s/grantium',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Гранты, стипендии и программы обмена для молодёжи СНГ.',
    ),
    dict(
        name='HTP Kyrgyzstan',
        source_type='telegram',
        identifier='htp_kyrgyzstan',
        url='https://t.me/s/htp_kyrgyzstan',
        config={'fetch_method': 'telegram_web_preview'},
        notes='High Tech Park Kyrgyzstan — IT-события, стажировки и вакансии.',
    ),
    dict(
        name='Geek Events',
        source_type='telegram',
        identifier='geekevents',
        url='https://t.me/s/geekevents',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Анонсы IT-событий, хакатонов и конференций.',
    ),
    dict(
        name='AI Kyrgyzstan',
        source_type='telegram',
        identifier='ai_kgz',
        url='https://t.me/s/ai_kgz',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Новости и события сообщества AI в Кыргызстане: хакатоны, митапы, обучение.',
    ),
    dict(
        name='StudyQA',
        source_type='telegram',
        identifier='studyqa',
        url='https://t.me/s/studyqa',
        config={'fetch_method': 'telegram_web_preview'},
        notes='Стипендии, гранты и обучение за рубежом.',
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
        ('aggregator', '0004_kg_sources_update'),
    ]

    operations = [
        migrations.RunPython(seed_sources, remove_sources),
    ]
