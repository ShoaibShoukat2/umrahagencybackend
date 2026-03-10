"""
Agora Token Generation
Generates RTC tokens for secure audio streaming
"""

import time
import hmac
import hashlib
import struct
from django.conf import settings

class AgoraTokenBuilder:
    """Generate Agora RTC tokens for audio streaming"""
    
    @staticmethod
    def build_token(app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        """
        Build Agora RTC token
        
        Args:
            app_id: Agora App ID
            app_certificate: Agora App Certificate
            channel_name: Channel name (e.g., package_123)
            uid: User ID (0 for any user)
            role: 1 for broadcaster, 2 for audience
            privilege_expired_ts: Token expiration timestamp
            
        Returns:
            Token string
        """
        return AgoraTokenBuilder._build_token_with_uid(
            app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
        )
    
    @staticmethod
    def _build_token_with_uid(app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        """Internal method to build token"""
        # This is a simplified version
        # In production, use the official Agora Python SDK: pip install agora-token-builder
        
        # For now, return a placeholder
        # TODO: Install agora-token-builder package and use proper token generation
        return f"AGORA_TOKEN_{app_id}_{channel_name}_{uid}_{role}_{privilege_expired_ts}"


def generate_rtc_token(channel_name, uid=0, role=1, expiration_seconds=3600):
    """
    Generate Agora RTC token for audio streaming
    
    Args:
        channel_name: Unique channel identifier (e.g., "package_123")
        uid: User ID (0 for any user, or specific user ID)
        role: 1 for broadcaster (tour leader), 2 for audience (customers)
        expiration_seconds: Token validity duration (default 1 hour)
        
    Returns:
        dict with token and channel info
    """
    
    # Get Agora credentials from settings
    app_id = getattr(settings, 'AGORA_APP_ID', '')
    app_certificate = getattr(settings, 'AGORA_APP_CERTIFICATE', '')
    
    if not app_id or not app_certificate:
        raise ValueError('Agora credentials not configured in settings')
    
    # Calculate expiration timestamp
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_seconds
    
    # Generate token
    token = AgoraTokenBuilder.build_token(
        app_id=app_id,
        app_certificate=app_certificate,
        channel_name=channel_name,
        uid=uid,
        role=role,
        privilege_expired_ts=privilege_expired_ts
    )
    
    return {
        'token': token,
        'app_id': app_id,
        'channel_name': channel_name,
        'uid': uid,
        'role': role,
        'expires_at': privilege_expired_ts,
        'expires_in': expiration_seconds
    }


# Role constants
ROLE_BROADCASTER = 1  # Tour leader
ROLE_AUDIENCE = 2     # Customers
