from django.db import migrations

# Timepad требует регистрацию API-токена для юр./физлиц РФ — недоступно для
# пользователей из других стран СНГ (в т.ч. Кыргызстана). Отключаем источник,
# но оставляем коллектор/конфиг на месте — можно будет включить вручную, если
# токен всё же станет доступен.
TIMEPAD_LOOKUP = dict(source_type='website', identifier='https://api.timepad.ru/v1/events')

TIMEPAD_INACTIVE = dict(
    is_active=False,
    notes='Официальный REST API Timepad — события по категориям и городам. '
          'Требуется API-токен (см. dev.timepad.ru), регистрация которого '
          'доступна только юр./физлицам РФ — недоступно для пользователей из '
          'других стран СНГ (в т.ч. Кыргызстана). Источник отключён; для '
          'Кыргызстана используется WordPress REST API Volunteer.kg.',
)

TIMEPAD_ACTIVE = dict(
    is_active=True,
    notes='Официальный REST API Timepad — события по категориям и городам. '
          'Требуется API-токен (см. dev.timepad.ru).',
)

# У Volunteer.kg отключены RSS-фиды (редиректят на главную), но WordPress
# REST API работает и без токена отдаёт полный текст постов в JSON —
# переключаем источник на него вместо html_scrape-заглушки.
VOLUNTEER_KG_LOOKUP = dict(source_type='website', identifier='https://volunteer.kg/en/project/')

VOLUNTEER_KG_NEW = dict(
    name='Volunteer.kg — поиск волонтёров',
    identifier='https://volunteer.kg/wp-json/wp/v2/posts?categories=16',
    url='https://volunteer.kg/category/poisk-volonterov/',
    config={
        'fetch_method': 'wordpress_api',
        'api_url': 'https://volunteer.kg/wp-json/wp/v2/posts',
        'params': {'categories': 16},
    },
    notes='WordPress REST API раздела «Поиск волонтёров» — основной портал '
          'волонтёрства Кыргызстана. Используется как источник, не '
          'требующий API-ключа, для региона СНГ/Кыргызстан (замена Timepad).',
)

VOLUNTEER_KG_OLD = dict(
    name='Volunteer.kg — проекты',
    identifier='https://volunteer.kg/en/project/',
    url='https://volunteer.kg/en/project/',
    config={'fetch_method': 'html_scrape'},
    notes='Портал волонтёрских проектов Кыргызстана.',
)


def forwards(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')

    Source.objects.filter(**TIMEPAD_LOOKUP).update(**TIMEPAD_INACTIVE)
    Source.objects.filter(**VOLUNTEER_KG_LOOKUP).update(**VOLUNTEER_KG_NEW)


def backwards(apps, schema_editor):
    Source = apps.get_model('aggregator', 'Source')

    Source.objects.filter(**TIMEPAD_LOOKUP).update(**TIMEPAD_ACTIVE)
    Source.objects.filter(
        source_type='website',
        identifier=VOLUNTEER_KG_NEW['identifier'],
    ).update(**VOLUNTEER_KG_OLD)


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0003_rawitem_published_at'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
