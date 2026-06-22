import logging

import requests as http_requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

User = get_user_model()

PROVIDERS = {
    'google': {
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'client_id_setting': 'GOOGLE_CLIENT_ID',
        'client_secret_setting': 'GOOGLE_CLIENT_SECRET',
        'id_field': 'google_id',
        'scope': 'openid email profile',
    },
    'github': {
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo_url': 'https://api.github.com/user',
        'emails_url': 'https://api.github.com/user/emails',
        'client_id_setting': 'GITHUB_CLIENT_ID',
        'client_secret_setting': 'GITHUB_CLIENT_SECRET',
        'id_field': 'github_id',
        'scope': 'read:user user:email',
    },
    'discord': {
        'token_url': 'https://discord.com/api/oauth2/token',
        'userinfo_url': 'https://discord.com/api/users/@me',
        'client_id_setting': 'DISCORD_CLIENT_ID',
        'client_secret_setting': 'DISCORD_CLIENT_SECRET',
        'id_field': 'discord_id',
        'scope': 'identify email',
    },
}


def _exchange_code(provider_cfg, code, redirect_uri):
    client_id = getattr(settings, provider_cfg['client_id_setting'], '')
    client_secret = getattr(settings, provider_cfg['client_secret_setting'], '')

    resp = http_requests.post(
        provider_cfg['token_url'],
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        },
        headers={'Accept': 'application/json'},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _get_userinfo_google(access_token):
    resp = http_requests.get(
        PROVIDERS['google']['userinfo_url'],
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        'provider_id': str(data['id']),
        'email': data.get('email', ''),
        'first_name': data.get('given_name', ''),
        'last_name': data.get('family_name', ''),
        'avatar_url': data.get('picture', ''),
    }


def _get_userinfo_github(access_token):
    headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
    resp = http_requests.get(
        PROVIDERS['github']['userinfo_url'], headers=headers, timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    email = data.get('email') or ''
    if not email:
        emails_resp = http_requests.get(
            PROVIDERS['github']['emails_url'], headers=headers, timeout=10,
        )
        if emails_resp.ok:
            for e in emails_resp.json():
                if e.get('primary') and e.get('verified'):
                    email = e['email']
                    break

    name = (data.get('name') or '').split(' ', 1)
    return {
        'provider_id': str(data['id']),
        'email': email,
        'first_name': name[0] if name else '',
        'last_name': name[1] if len(name) > 1 else '',
        'avatar_url': data.get('avatar_url', ''),
    }


def _get_userinfo_discord(access_token):
    resp = http_requests.get(
        PROVIDERS['discord']['userinfo_url'],
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    name = (data.get('global_name') or data.get('username') or '').split(' ', 1)
    avatar_url = ''
    if data.get('avatar'):
        avatar_url = f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png"

    return {
        'provider_id': str(data['id']),
        'email': data.get('email', ''),
        'first_name': name[0] if name else '',
        'last_name': name[1] if len(name) > 1 else '',
        'avatar_url': avatar_url,
    }


USERINFO_FETCHERS = {
    'google': _get_userinfo_google,
    'github': _get_userinfo_github,
    'discord': _get_userinfo_discord,
}


def _get_or_create_user(provider_name, userinfo):
    provider_cfg = PROVIDERS[provider_name]
    id_field = provider_cfg['id_field']
    provider_id = userinfo['provider_id']
    email = userinfo['email'].lower()

    user = User.objects.filter(**{id_field: provider_id}).first()
    if user:
        return user

    if email:
        user = User.objects.filter(email=email).first()
        if user:
            setattr(user, id_field, provider_id)
            user.save(update_fields=[id_field])
            return user

    if not email:
        return None

    user = User.objects.create(
        email=email,
        username=email,
        first_name=userinfo.get('first_name', '')[:150],
        last_name=userinfo.get('last_name', '')[:150],
        is_active=True,
        email_verified=True,
        **{id_field: provider_id},
    )
    user.set_unusable_password()
    user.save()
    return user


def _jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class SocialAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, provider):
        if provider not in PROVIDERS:
            return Response(
                {'detail': f'Unknown provider: {provider}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        if not code or not redirect_uri:
            return Response(
                {'detail': 'code and redirect_uri are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider_cfg = PROVIDERS[provider]

        try:
            access_token = _exchange_code(provider_cfg, code, redirect_uri)
        except Exception:
            logger.exception('OAuth token exchange failed for %s', provider)
            return Response(
                {'detail': 'Failed to exchange authorization code'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            userinfo = USERINFO_FETCHERS[provider](access_token)
        except Exception:
            logger.exception('Failed to fetch user info from %s', provider)
            return Response(
                {'detail': 'Failed to fetch user info from provider'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = _get_or_create_user(provider, userinfo)
        if user is None:
            return Response(
                {'detail': 'Could not determine email from provider. Please use email registration.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = _jwt_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class SocialAuthConfigView(APIView):
    """Returns OAuth client IDs for frontend (public, no secrets)."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'google': {
                'client_id': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
                'scope': PROVIDERS['google']['scope'],
            },
            'github': {
                'client_id': getattr(settings, 'GITHUB_CLIENT_ID', ''),
                'scope': PROVIDERS['github']['scope'],
            },
            'discord': {
                'client_id': getattr(settings, 'DISCORD_CLIENT_ID', ''),
                'scope': PROVIDERS['discord']['scope'],
            },
        })
