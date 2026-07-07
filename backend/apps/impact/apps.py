from django.apps import AppConfig


class ImpactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.impact'
    verbose_name = 'Social Impact Analytics'

    def ready(self):
        import apps.impact.signals  # noqa
