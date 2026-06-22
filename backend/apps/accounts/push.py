import json
import logging

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

User = get_user_model()


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return f'{self.user.email} - {self.endpoint[:50]}'

    def to_webpush(self):
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth,
            },
        }


class PushSubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sub = request.data.get('subscription', {})
        endpoint = sub.get('endpoint')
        keys = sub.get('keys', {})

        if not endpoint or not keys.get('p256dh') or not keys.get('auth'):
            return Response({'detail': 'Invalid subscription'}, status=status.HTTP_400_BAD_REQUEST)

        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': keys['p256dh'],
                'auth': keys['auth'],
            },
        )
        return Response({'detail': 'Subscribed'})

    def delete(self, request):
        endpoint = request.data.get('endpoint')
        if endpoint:
            PushSubscription.objects.filter(endpoint=endpoint, user=request.user).delete()
        return Response({'detail': 'Unsubscribed'})


class VapidPublicKeyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'public_key': settings.VAPID_PUBLIC_KEY})


def send_push_to_all(title, body, url='/opportunities'):
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning('pywebpush not installed')
        return 0

    if not settings.VAPID_PRIVATE_KEY:
        return 0

    payload = json.dumps({'title': title, 'body': body, 'url': url})
    sent = 0

    for sub in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info=sub.to_webpush(),
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': settings.VAPID_ADMIN_EMAIL},
            )
            sent += 1
        except Exception as e:
            if '410' in str(e) or '404' in str(e):
                sub.delete()
            else:
                logger.warning('Push failed for %s: %s', sub.endpoint[:50], e)

    return sent
