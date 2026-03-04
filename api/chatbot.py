"""
AI Chatbot with Google Gemini Integration
"""
import os
import json
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Package, Booking, Customer
from django.utils import timezone
from datetime import datetime

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}'


def get_database_context():
    """Get relevant data from database for AI context"""
    try:
        # Get packages
        packages = Package.objects.filter(is_active=True)[:10]
        packages_data = []
        
        for pkg in packages:
            packages_data.append({
                'name': pkg.name,
                'category': pkg.category.name if pkg.category else 'N/A',
                'price_from': float(pkg.room_prices.order_by('price').first().price) if pkg.room_prices.exists() else 0,
                'duration': f"{pkg.duration_days} days / {pkg.duration_nights} nights",
                'travel_date': pkg.travel_date.strftime('%d %b %Y'),
                'location': pkg.location,
            })
        
        context = {
            'company': {
                'name': 'TM Fouzy Travel & Tours Pte Ltd',
                'phone': '+65 6294 8044',
                'email': 'enquiry@tmfouzy.sg',
                'whatsapp': '+65 9820 1134',
                'address': '390 Victoria St #03-15, Singapore 188061',
                'uen': '199402129H'
            },
            'packages': packages_data,
            'services': [
                'Umrah packages',
                'Hajj packages',
                'Ziarah tours',
                'Holiday packages',
                'Visa assistance',
                'Travel insurance'
            ],
            'payment_methods': ['PayNow', 'Credit Card', 'Bank Transfer', 'PayPal'],
            'room_types': ['Single', 'Double Sharing', 'Triple Sharing', 'Quad Sharing']
        }
        
        return context
    except Exception as e:
        print(f"Error getting database context: {e}")
        return {}


@api_view(['POST'])
def chat_with_ai(request):
    """
    Chat endpoint that uses Google Gemini AI
    """
    try:
        user_message = request.data.get('message', '')
        
        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Gemini API key is configured
        if not GEMINI_API_KEY:
            # Fallback to rule-based responses
            return Response({
                'response': get_fallback_response(user_message),
                'source': 'fallback'
            })
        
        # Get database context
        db_context = get_database_context()
        
        # Create system prompt with database context
        system_prompt = f"""You are a helpful travel assistant for TM Fouzy Travel & Tours, a Singapore-based travel agency specializing in Umrah, Hajj, and Islamic tours.

Company Information:
- Name: {db_context['company']['name']}
- Phone: {db_context['company']['phone']}
- Email: {db_context['company']['email']}
- WhatsApp: {db_context['company']['whatsapp']}
- Address: {db_context['company']['address']}

Available Packages:
{json.dumps(db_context['packages'], indent=2)}

Services: {', '.join(db_context['services'])}
Payment Methods: {', '.join(db_context['payment_methods'])}
Room Types: {', '.join(db_context['room_types'])}

Guidelines:
1. Be friendly, professional, and helpful
2. Use the package information provided above
3. Provide accurate prices and dates from the data
4. If asked about booking, guide them through the process
5. For specific inquiries, provide contact information
6. Keep responses concise but informative
7. Use emojis appropriately to make responses friendly
8. Always mention "Assalamu Alaikum" when greeting

User Question: {user_message}

Provide a helpful response based on the information above."""

        # Call Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": system_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            
            return Response({
                'response': ai_response,
                'source': 'gemini'
            })
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            # Fallback to rule-based
            return Response({
                'response': get_fallback_response(user_message),
                'source': 'fallback'
            })
            
    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        return Response({
            'response': get_fallback_response(request.data.get('message', '')),
            'source': 'fallback'
        }, status=status.HTTP_200_OK)


def get_fallback_response(message):
    """Fallback rule-based responses when AI is not available"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'assalam', 'salam']):
        return "Assalamu Alaikum! 👋 Welcome to TM Fouzy Travel & Tours. How can I assist you with your Umrah or Hajj journey today?"
    
    elif any(word in message_lower for word in ['package', 'umrah', 'hajj']):
        return "We offer various Umrah and Hajj packages starting from $1800 per person. Our packages include accommodation, transportation, and visa assistance. Would you like to know more about specific packages?"
    
    elif any(word in message_lower for word in ['price', 'cost', 'how much']):
        return "Our packages start from $1800 per person. Prices vary based on:\n• Room sharing type\n• Travel dates\n• Package duration\n• Additional services\n\nContact us for detailed pricing: +65 6294 8044"
    
    elif any(word in message_lower for word in ['contact', 'phone', 'email', 'whatsapp']):
        return "Contact Us:\n📞 Phone: +65 6294 8044\n📧 Email: enquiry@tmfouzy.sg\n💬 WhatsApp: +65 9820 1134\n📍 Address: 390 Victoria St #03-15, Singapore 188061"
    
    elif any(word in message_lower for word in ['book', 'booking', 'reserve']):
        return "To book a package:\n1. Browse our packages\n2. Select your preferred package\n3. Choose room type\n4. Fill passenger details\n5. Make payment\n\nNeed help? Call us at +65 6294 8044"
    
    else:
        return "Thank you for your message! For detailed assistance, please:\n📞 Call: +65 6294 8044\n📧 Email: enquiry@tmfouzy.sg\n💬 WhatsApp: +65 9820 1134\n\nOur team is ready to help you!"
