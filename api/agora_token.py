"""
Agora Token Generation using agora-token-builder
pip install agora-token-builder
"""
import time
from django.conf import settings

ROLE_BROADCASTER = 1
ROLE_AUDIENCE = 2

def generate_rtc_token(channel_name, uid=0, role=1, expiration_seconds=7200):
    app_id = getattr(settings, 'AGORA_APP_ID', '')
    app_certificate = getattr(settings, 'AGORA_APP_CERTIFICATE', '')

    if not app_id:
        raise ValueError('AGORA_APP_ID not configured')

    privilege_expired_ts = int(time.time()) + expiration_seconds

    # Try official SDK first
    try:
        from agora_token_builder import RtcTokenBuilder
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
        )
    except ImportError:
        # Fallback: use app_id as token (works with Agora in test mode / no certificate)
        token = app_id

    return {
        'token': token,
        'app_id': app_id,
        'channel_name': channel_name,
        'uid': uid,
        'role': role,
        'expires_in': expiration_seconds,
    }
