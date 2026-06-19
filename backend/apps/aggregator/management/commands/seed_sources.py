"""
Добавляет дополнительные источники в агрегатор: RSS-фиды, сайты, Telegram-каналы.
Идемпотентна — повторный запуск не создаёт дубликатов.
"""

from django.core.management.base import BaseCommand

from apps.aggregator.models import Source, SourceTrustLevel, SourceType

SOURCES = [
    # ── RSS-фиды ──────────────────────────────────────────────
    {
        'name': 'Добро.рф — новости',
        'source_type': SourceType.RSS,
        'identifier': 'https://dobro.ru/rss',
        'url': 'https://dobro.ru/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },
    {
        'name': 'Теплица социальных технологий',
        'source_type': SourceType.RSS,
        'identifier': 'https://te-st.org/feed/',
        'url': 'https://te-st.org/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },
    {
        'name': 'Habr — волонтёрство и social',
        'source_type': SourceType.RSS,
        'identifier': 'https://habr.com/ru/rss/hub/social/',
        'url': 'https://habr.com/ru/hub/social/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Leader-ID — события',
        'source_type': SourceType.RSS,
        'identifier': 'https://leader-id.ru/events/rss',
        'url': 'https://leader-id.ru/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },
    {
        'name': 'Молодёжь России — новости',
        'source_type': SourceType.RSS,
        'identifier': 'https://fadm.gov.ru/rss',
        'url': 'https://fadm.gov.ru/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },
    {
        'name': 'Grants.kz (RSS)',
        'source_type': SourceType.RSS,
        'identifier': 'https://grants.kz/feed/',
        'url': 'https://grants.kz/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },

    # ── Сайты (HTML scraping) ────────────────────────────────
    {
        'name': 'Волонтёр.рф — проекты',
        'source_type': SourceType.WEBSITE,
        'identifier': 'https://xn--90acesaqsbbbreoa.xn--p1ai/projects',
        'url': 'https://xn--90acesaqsbbbreoa.xn--p1ai/',
        'config': {
            'fetch_method': 'html_scrape',
            'article_selector': '.project-card, .card, article',
            'title_selector': 'h3 a, h2 a, .card-title a, h3, h2',
        },
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'IT-события (it-events.com)',
        'source_type': SourceType.WEBSITE,
        'identifier': 'https://it-events.com/events?type=hackathon&online=true',
        'url': 'https://it-events.com/',
        'config': {
            'fetch_method': 'html_scrape',
            'article_selector': '.event-card, .event-list-item, article',
            'title_selector': 'a.event-card__title, h3 a, h2 a',
        },
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Конкурсы и гранты (rsv.ru)',
        'source_type': SourceType.WEBSITE,
        'identifier': 'https://rsv.ru/competitions/',
        'url': 'https://rsv.ru/',
        'config': {
            'fetch_method': 'html_scrape',
            'article_selector': '.competition-card, .card, article',
            'title_selector': 'h3 a, .card-title a, h2 a, h3, h2',
        },
        'trust_level': SourceTrustLevel.TRUSTED,
    },

    # ── WordPress API ────────────────────────────────────────
    {
        'name': 'ASA Kyrgyzstan — блог',
        'source_type': SourceType.WEBSITE,
        'identifier': 'https://asa.kg/wp-json/wp/v2/posts',
        'url': 'https://asa.kg/',
        'config': {
            'fetch_method': 'wordpress_api',
            'api_url': 'https://asa.kg/wp-json/wp/v2/posts',
        },
        'trust_level': SourceTrustLevel.QUARANTINE,
    },

    # ── Дополнительные Telegram-каналы ───────────────────────
    {
        'name': 'Волонтёрство KG',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'volunteer_kg',
        'url': 'https://t.me/s/volunteer_kg',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Стажировки и практики',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'internships_russia',
        'url': 'https://t.me/s/internships_russia',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Гранты и конкурсы РФ',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'grants_rf',
        'url': 'https://t.me/s/grants_rf',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'DevBy — IT-события',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'devaborig',
        'url': 'https://t.me/s/devaborig',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Молодёжная политика',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'youthpolicyru',
        'url': 'https://t.me/s/youthpolicyru',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
    {
        'name': 'Scholarship Global',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'scholarship_global',
        'url': 'https://t.me/s/scholarship_global',
        'config': {'fetch_method': 'telegram_web_preview'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
]


class Command(BaseCommand):
    help = 'Добавляет дополнительные источники в агрегатор (идемпотентно)'

    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for src in SOURCES:
            _, was_created = Source.objects.get_or_create(
                identifier=src['identifier'],
                defaults={
                    'name': src['name'],
                    'source_type': src['source_type'],
                    'url': src.get('url', ''),
                    'config': src.get('config', {}),
                    'trust_level': src.get('trust_level', SourceTrustLevel.QUARANTINE),
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f'Done: {created} created, {skipped} already existed')
        )
