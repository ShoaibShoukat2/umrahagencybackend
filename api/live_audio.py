"""
Live Audio Streaming Views
Handles live audio broadcasting and push notifications
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import LiveAudioSession, Package, Customer, Booking
from .agora_token import generate_rtc_token, ROLE_BROADCASTER, ROLE_AUDIENCE
import requests
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])
def start_live_audio(request):
    """
    Tour leader starts a live audio broadcast
    
    Request body:
    {
        "package_id": 123,
        "tour_leader_email": "leader@example.com",
        "title": "Morning Briefing"
    }
    """
    try:
        package_id = request.data.get('package_id')
        tour_leader_email = request.data.get('tour_leader_email')
        title = request.data.get('title', 'Live Audio from Tour Leader')
        
        if not package_id or not tour_leader_email:
            return Response(
                {'error': 'package_id and tour_leader_email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get package
        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response(
                {'error': 'Package not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify tour leader
        # In production, add proper authentication check
        
        # Generate channel name
        channel_name = f"package_{package_id}_{int(timezone.now().timestamp())}"
        
        # Generate Agora token for broadcaster (tour leader)
        token_data = generate_rtc_token(
            channel_name=channel_name,
            uid=0,  # 0 means any user can use this token
            role=ROLE_BROADCASTER,
            expiration_seconds=7200  # 2 hours
        )
        
        # Create live audio session
        session = LiveAudioSession.objects.create(
            package=package,
            channel_name=channel_name,
            title=title,
            tour_leader_email=tour_leader_email,
            status='active',
            started_at=timezone.now()
        )
        
        # Get all customers in this package
        bookings = Booking.objects.filter(package=package, status__in=['confirmed', 'pending'])
        customer_emails = [booking.customer.email for booking in bookings]
        
        # Send push notifications to all customers
        send_live_audio_notification(
            package_id=package_id,
            channel_name=channel_name,
            title=title,
            customer_emails=customer_emails
        )
        
        return Response({
            'success': True,
            'session_id': session.id,
            'channel_name': channel_name,
            'token': token_data['token'],
            'app_id': token_data['app_id'],
            'expires_in': token_data['expires_in'],
            'customers_notified': len(customer_emails),
            'message': f'Live audio started. {len(customer_emails)} customers notified.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def join_live_audio(request):
    """
    Customer joins a live audio session
    
    Request body:
    {
        "session_id": 123,
        "customer_email": "customer@example.com"
    }
    """
    try:
        session_id = request.data.get('session_id')
        customer_email = request.data.get('customer_email')
        
        if not session_id or not customer_email:
            return Response(
                {'error': 'session_id and customer_email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get session
        try:
            session = LiveAudioSession.objects.get(id=session_id)
        except LiveAudioSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session is active
        if session.status != 'active':
            return Response(
                {'error': 'Session is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify customer is in the package
        customer = Customer.objects.filter(email=customer_email).first()
        if not customer:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        booking = Booking.objects.filter(
            customer=customer,
            package=session.package,
            status__in=['confirmed', 'pending']
        ).first()
        
        if not booking:
            return Response(
                {'error': 'You are not authorized to join this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate Agora token for audience (customer)
        token_data = generate_rtc_token(
            channel_name=session.channel_name,
            uid=0,
            role=ROLE_AUDIENCE,
            expiration_seconds=7200  # 2 hours
        )
        
        # Increment listener count
        session.listener_count += 1
        session.save()
        
        return Response({
            'success': True,
            'session_id': session.id,
            'channel_name': session.channel_name,
            'token': token_data['token'],
            'app_id': token_data['app_id'],
            'title': session.title,
            'started_at': session.started_at,
            'listener_count': session.listener_count,
            'expires_in': token_data['expires_in']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def end_live_audio(request):
    """
    Tour leader ends a live audio broadcast
    
    Request body:
    {
        "session_id": 123
    }
    """
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get session
        try:
            session = LiveAudioSession.objects.get(id=session_id)
        except LiveAudioSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # End session
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save()
        
        return Response({
            'success': True,
            'message': 'Live audio session ended',
            'duration_minutes': (session.ended_at - session.started_at).total_seconds() / 60,
            'total_listeners': session.listener_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_sessions(request):
    """
    Get all active live audio sessions for a package
    
    Query params:
    - package_id: Package ID
    """
    try:
        package_id = request.query_params.get('package_id')
        
        if not package_id:
            return Response(
                {'error': 'package_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sessions = LiveAudioSession.objects.filter(
            package_id=package_id,
            status='active'
        ).order_by('-started_at')
        
        sessions_data = [{
            'id': session.id,
            'channel_name': session.channel_name,
            'title': session.title,
            'started_at': session.started_at,
            'listener_count': session.listener_count,
            'tour_leader_email': session.tour_leader_email
        } for session in sessions]
        
        return Response({
            'success': True,
            'sessions': sessions_data,
            'count': len(sessions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def send_live_audio_notification(package_id, channel_name, title, customer_emails):
    """
    Send push notification to customers via Firebase Cloud Messaging
    
    Args:
        package_id: Package ID
        channel_name: Agora channel name
        title: Broadcast title
        customer_emails: List of customer emails
    """
    try:
        # Get Firebase Server Key from settings
        fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', '')
        
        if not fcm_server_key:
            print('Warning: FCM_SERVER_KEY not configured')
            return
        
        # FCM API endpoint
        fcm_url = 'https://fcm.googleapis.com/fcm/send'
        
        # Notification payload
        notification_data = {
            'to': f'/topics/package_{package_id}',  # Send to package topic
            'notification': {
                'title': '🔴 Tour Leader is Live!',
                'body': title,
                'sound': 'default',
                'priority': 'high'
            },
            'data': {
                'type': 'live_audio',
                'channel_name': channel_name,
                'package_id': str(package_id),
                'title': title
            }
        }
        
        headers = {
            'Authorization': f'key={fcm_server_key}',
            'Content-Type': 'application/json'
        }
        
        # Send notification
        response = requests.post(fcm_url, json=notification_data, headers=headers)
        
        if response.status_code == 200:
            print(f'✅ Push notification sent to package_{package_id}')
        else:
            print(f'❌ Failed to send push notification: {response.text}')
            
    except Exception as e:
        print(f'❌ Error sending push notification: {str(e)}')
