"""
Celery configuration for Nachalo Rosta project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('nachalo_rosta')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-event-deadlines': {
        'task': 'apps.events.tasks.check_event_deadlines',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-achievement-notifications': {
        'task': 'apps.achievements.tasks.send_pending_notifications',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'calculate-impact-stats': {
        'task': 'apps.impact.tasks.calculate_impact_statistics',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'cleanup-expired-tokens': {
        'task': 'apps.accounts.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-event-recommendations': {
        'task': 'apps.recommendations.tasks.generate_recommendations_for_all_users',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
