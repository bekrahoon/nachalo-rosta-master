from django.db import migrations

# Оставляем только IT-источники вне России и без волонтёрских программ.
KEEP_IDENTIFIERS = [
    # Telegram — Кыргызстан IT
    'htp_kyrgyzstan',
    'ai_kgz',
    'itcommunity_bishkek',
    'edugrant_kg',
    # Telegram — Казахстан IT
    'it_kazakhstan',
    'hackathons_kz',
    # Telegram — Узбекистан IT
    'itpark_uz',
    # Telegram — международные IT / гранты / стажировки
    'global_hackathons',
    'geekevents',
    'devaborig',
    'talentedyoung',
    'grantium',
    'studyqa',
    # Сайты — IT
    'https://hackathons.pro/',
    'https://it-events.com/events?type=hackathon&online=true',
]


def forwards(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')
    Source.objects.exclude(identifier__in=KEEP_IDENTIFIERS).delete()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0006_hackathon_sources'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
