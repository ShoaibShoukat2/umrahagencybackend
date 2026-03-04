from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer
import random
import string
from datetime import datetime, timedelta

# Store OTPs temporarily (in production, use Redis or database)
otp_storage = {}

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP via email"""
    try:
        subject = 'Your OTP for Umrah Agency'
        message = f'''
        Your OTP for verification is: {otp}
        
        This OTP is valid for 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Umrah Agency Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    phone = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    postal_code = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register new user and send OTP"""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    email = data['email']
    
    # Check if user already exists
    if User.objects.filter(username=email).exists():
        return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP with expiry (10 minutes)
    otp_storage[email] = {
        'otp': otp,
        'expiry': datetime.now() + timedelta(minutes=10),
        'user_data': data,
        'verified': False
    }
    
    # Send OTP via email
    if send_otp_email(email, otp):
        return Response({
            'message': 'OTP sent to your email. Please verify to complete registration.',
            'email': email,
            'otp': otp  # Remove this in production! Only for testing
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Failed to send OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP and create user account"""
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    
    # Check if OTP exists
    if email not in otp_storage:
        return Response({'error': 'No OTP found for this email. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    
    stored_data = otp_storage[email]
    
    # Check if OTP expired
    if datetime.now() > stored_data['expiry']:
        del otp_storage[email]
        return Response({'error': 'OTP expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify OTP
    if stored_data['otp'] != otp:
        return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user account
    user_data = stored_data['user_data']
    try:
        # Create Django user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=user_data['password'],
            first_name=user_data['name']
        )
        
        # Create Customer profile
        customer = Customer.objects.create(
            user=user,
            email=email,
            phone=user_data['phone'],
            address=user_data['address'],
            postal_code=user_data['postal_code']
        )
        
        # Mark as verified and clean up
        del otp_storage[email]
        
        return Response({
            'message': 'Registration successful! You can now login.',
            'user': {
                'email': email,
                'name': user_data['name']
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Failed to create account: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    # Authenticate user
    user = authenticate(username=email, password=password)
    
    if user is None:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get customer profile
    try:
        customer = Customer.objects.get(user=user)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name,
                'phone': customer.phone,
                'address': customer.address,
                'postal_code': customer.postal_code
            }
        }, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name
            }
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    """Request OTP for password reset or verification"""
    serializer = OTPRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Check if user exists
    if not User.objects.filter(username=email).exists():
        return Response({'error': 'No account found with this email'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP
    otp_storage[email] = {
        'otp': otp,
        'expiry': datetime.now() + timedelta(minutes=10),
        'type': 'password_reset'
    }
    
    # Send OTP
    if send_otp_email(email, otp):
        return Response({
            'message': 'OTP sent to your email',
            'email': email,
            'otp': otp  # Remove in production
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with OTP"""
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    
    if not all([email, otp, new_password]):
        return Response({'error': 'Email, OTP, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify OTP
    if email not in otp_storage:
        return Response({'error': 'No OTP found. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    
    stored_data = otp_storage[email]
    
    if datetime.now() > stored_data['expiry']:
        del otp_storage[email]
        return Response({'error': 'OTP expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if stored_data['otp'] != otp:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Reset password
    try:
        user = User.objects.get(username=email)
        user.set_password(new_password)
        user.save()
        
        del otp_storage[email]
        
        return Response({'message': 'Password reset successful. You can now login with your new password.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Admin login endpoint - authenticates Django admin users
    """
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is staff/admin
    if not user.is_staff:
        return Response({'error': 'Access denied. Admin privileges required.'}, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'message': 'Login successful',
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'token': 'admin-token-placeholder'  # Add proper token generation if needed
    }, status=status.HTTP_200_OK)
