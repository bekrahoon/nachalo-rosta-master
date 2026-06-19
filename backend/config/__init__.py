import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('nachalo_rosta')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'apps.accounts.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),
    },
    'generate-recommendations': {
        'task': 'apps.recommendations.tasks.generate_recommendations_for_all_users',
        'schedule': crontab(hour=3, minute=0),
    },
    'aggregator-poll-sources': {
        'task': 'apps.aggregator.tasks.poll_due_sources',
        'schedule': crontab(minute='*/15'),
    },
    'aggregator-classify': {
        'task': 'apps.aggregator.tasks.classify_pending_items',
        'schedule': crontab(minute='*/10'),
    },
}
