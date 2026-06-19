"""
Добавляет международные (не-РФ) источники: Кыргызстан, Казахстан, Узбекистан,
международные платформы волонтёрства, стипендии, хакатоны.
"""

from django.core.management.base import BaseCommand

from apps.aggregator.models import Source, SourceTrustLevel, SourceType

SOURCES = [
    # ── Кыргызстан: Telegram ─────────────────────────────────
    {
        'name': 'Стажировки и вакансии KG',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'job_kg',
        'url': 'https://t.me/s/job_kg',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'IT Community Bishkek',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'itcommunity_bishkek',
        'url': 'https://t.me/s/itcommunity_bishkek',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Бишкек волонтёры',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'bishkek_volunteers',
        'url': 'https://t.me/s/bishkek_volunteers',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'AUCA Events',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'auca_events',
        'url': 'https://t.me/s/auca_events',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'KG Opportunities',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'kg_opportunities',
        'url': 'https://t.me/s/kg_opportunities',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Гранты Кыргызстан',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'granty_kyrgyzstan',
        'url': 'https://t.me/s/granty_kyrgyzstan',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Youth of Kyrgyzstan',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'youthofkg',
        'url': 'https://t.me/s/youthofkg',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'UN Kyrgyzstan',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'un_kyrgyzstan',
        'url': 'https://t.me/s/un_kyrgyzstan',
        'config': {'fetch_method': 'telegram_web_preview'},
    },

    # ── Казахстан: Telegram ──────────────────────────────────
    {
        'name': 'Стажировки Казахстан',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'internship_kz',
        'url': 'https://t.me/s/internship_kz',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Волонтёры Казахстан',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'volunteers_kz',
        'url': 'https://t.me/s/volunteers_kz',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'IT Kazakhstan',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'it_kazakhstan',
        'url': 'https://t.me/s/it_kazakhstan',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Гранты и стипендии KZ',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'grants_kz_channel',
        'url': 'https://t.me/s/grants_kz_channel',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Hackathons Kazakhstan',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'hackathons_kz',
        'url': 'https://t.me/s/hackathons_kz',
        'config': {'fetch_method': 'telegram_web_preview'},
    },

    # ── Узбекистан: Telegram ─────────────────────────────────
    {
        'name': 'IT Park Uzbekistan',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'itpark_uz',
        'url': 'https://t.me/s/itpark_uz',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Гранты Узбекистан',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'grants_uzbekistan',
        'url': 'https://t.me/s/grants_uzbekistan',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Стипендии и обучение UZ',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'scholarship_uz',
        'url': 'https://t.me/s/scholarship_uz',
        'config': {'fetch_method': 'telegram_web_preview'},
    },

    # ── Международные: Telegram ──────────────────────────────
    {
        'name': 'Scholarships & Grants',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'scholarships_grants',
        'url': 'https://t.me/s/scholarships_grants',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'DAAD Scholarships',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'daaborig',
        'url': 'https://t.me/s/daaborig',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Erasmus+ Opportunities',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'erasmus_opportunities',
        'url': 'https://t.me/s/erasmus_opportunities',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'International Internships',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'internships_abroad',
        'url': 'https://t.me/s/internships_abroad',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Global Hackathons',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'global_hackathons',
        'url': 'https://t.me/s/global_hackathons',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Volunteer Abroad',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'volunteer_abroad',
        'url': 'https://t.me/s/volunteer_abroad',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Study Abroad Central Asia',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'studyabroad_ca',
        'url': 'https://t.me/s/studyabroad_ca',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Youth Opportunities',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'youth_opportunities',
        'url': 'https://t.me/s/youth_opportunities',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Fully Funded Scholarships',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'fullyfundedscholarships',
        'url': 'https://t.me/s/fullyfundedscholarships',
        'config': {'fetch_method': 'telegram_web_preview'},
    },
    {
        'name': 'Central Asia Youth',
        'source_type': SourceType.TELEGRAM,
        'identifier': 'centralasia_youth',
        'url': 'https://t.me/s/centralasia_youth',
        'config': {'fetch_method': 'telegram_web_preview'},
    },

    # ── Сайты: HTML scraping ─────────────────────────────────
    {
        'name': 'Hackathons.pro',
        'source_type': SourceType.WEBSITE,
        'identifier': 'https://hackathons.pro/',
        'url': 'https://hackathons.pro/',
        'config': {
            'fetch_method': 'html_scrape',
            'article_selector': '.hackathon-card, .event-card, article, .card',
            'title_selector': 'h2 a, h3 a, .title a, h2, h3',
        },
    },

    # ── RSS ───────────────────────────────────────────────────
    {
        'name': 'UN Volunteers News',
        'source_type': SourceType.RSS,
        'identifier': 'https://www.unv.org/rss.xml',
        'url': 'https://www.unv.org/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.TRUSTED,
    },
    {
        'name': 'Devex — Development Jobs',
        'source_type': SourceType.RSS,
        'identifier': 'https://www.devex.com/news/rss',
        'url': 'https://www.devex.com/',
        'config': {'fetch_method': 'rss_feed'},
        'trust_level': SourceTrustLevel.QUARANTINE,
    },
]


class Command(BaseCommand):
    help = 'Добавляет международные источники (не-РФ)'

    def handle(self, *args, **options):
        created = 0
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

        self.stdout.write(self.style.SUCCESS(f'Created {created} international sources'))
