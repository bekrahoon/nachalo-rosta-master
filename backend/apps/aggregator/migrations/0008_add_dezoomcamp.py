from django.db import migrations


def forwards(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')
    Source.objects.update_or_create(
        source_type='telegram',
        identifier='dezoomcamp',
        defaults={
            'name': 'DataTalks.Club — ZoomCamp',
            'url': 'https://t.me/s/dezoomcamp',
            'config': {'fetch_method': 'telegram_web_preview'},
            'trust_level': 'quarantine',
            'is_active': True,
        },
    )


def backwards(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')
    Source.objects.filter(source_type='telegram', identifier='dezoomcamp').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0007_remove_non_it_sources'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
