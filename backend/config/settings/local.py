"""
Local Django settings for development.
"""

from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend для разработки (выводит в консоль)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Отключаем некоторые security checks в разработке
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Sentry отключён в разработке
SENTRY_DSN = None

# SQL queries logging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}
