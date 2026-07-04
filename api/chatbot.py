"""
AI Chatbot with Google Gemini Integration
"""
import os
import json
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Package

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()

# Prefer current models; fall back if one is unavailable
GEMINI_MODELS = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-pro',
]


def _company_info():
    return {
        'name': 'TM Fouzy Travel & Tours Pte Ltd',
        'phone': '+65 6294 8044',
        'email': 'enquiry@tmfouzy.sg',
        'whatsapp': '+65 9820 1134',
        'address': '390 Victoria St #03-15, Singapore 188061',
        'uen': '199402129H',
    }


def get_database_context():
    """Get relevant data from database for AI context"""
    packages_data = []
    try:
        packages = Package.objects.filter(is_active=True).select_related('category').prefetch_related('room_prices')[:15]
        for pkg in packages:
            min_price = 0
            room_price = pkg.room_prices.filter(available=True).order_by('price').first()
            if room_price:
                min_price = float(room_price.price)

            packages_data.append({
                'name': pkg.name,
                'category': pkg.category.name if pkg.category else 'N/A',
                'price_from': min_price,
                'duration': f"{pkg.duration_days} days / {pkg.duration_nights} nights",
                'travel_date': pkg.travel_date.strftime('%d %b %Y') if pkg.travel_date else 'TBA',
                'location': pkg.location or 'N/A',
                'hotel': pkg.hotel_name or '',
                'short_description': (pkg.short_description or '')[:200],
            })
    except Exception as e:
        print(f"Error getting package context: {e}")

    return {
        'company': _company_info(),
        'packages': packages_data,
        'services': [
            'Umrah packages',
            'Hajj packages',
            'Ziarah tours',
            'Holiday packages',
            'Visa assistance',
            'Travel insurance',
        ],
        'payment_methods': ['PayNow', 'Credit Card', 'Bank Transfer', 'PayPal'],
        'room_types': ['Single', 'Double Sharing', 'Triple Sharing', 'Quad Sharing'],
    }


def _call_gemini(system_prompt):
    """Call Gemini API, trying current models in order."""
    if not GEMINI_API_KEY:
        return None

    payload = {
        "contents": [{
            "parts": [{"text": system_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    headers = {'Content-Type': 'application/json'}

    for model in GEMINI_MODELS:
        url = (
            f'https://generativelanguage.googleapis.com/v1beta/models/'
            f'{model}:generateContent?key={GEMINI_API_KEY}'
        )
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            if response.status_code == 200:
                result = response.json()
                candidates = result.get('candidates') or []
                if not candidates:
                    continue
                parts = candidates[0].get('content', {}).get('parts') or []
                if parts and parts[0].get('text'):
                    return parts[0]['text']
            else:
                print(f"Gemini {model} error: {response.status_code} - {response.text[:300]}")
        except Exception as e:
            print(f"Gemini {model} request failed: {e}")

    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_ai(request):
    """
    Chat endpoint that uses Google Gemini AI with live package data.
    Falls back to rule-based answers when Gemini is unavailable.
    """
    try:
        user_message = (request.data.get('message') or '').strip()

        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        db_context = get_database_context()
        company = db_context['company']

        system_prompt = f"""You are a helpful travel assistant for TM Fouzy Travel & Tours, a Singapore-based travel agency specializing in Umrah, Hajj, and Islamic tours.

Company Information:
- Name: {company['name']}
- Phone: {company['phone']}
- Email: {company['email']}
- WhatsApp: {company['whatsapp']}
- Address: {company['address']}

Available Packages:
{json.dumps(db_context['packages'], indent=2)}

Services: {', '.join(db_context['services'])}
Payment Methods: {', '.join(db_context['payment_methods'])}
Room Types: {', '.join(db_context['room_types'])}

Guidelines:
1. Be friendly, professional, and helpful
2. Use the package information provided above — quote real names, prices, and dates when available
3. Provide accurate prices and dates from the data
4. If asked about booking, guide them to browse packages on the website and complete booking online
5. For specific inquiries, provide contact information
6. Keep responses concise but informative
7. Use emojis appropriately to make responses friendly
8. Greet with "Assalamu Alaikum" when the user greets you
9. Prices are in SGD (Singapore Dollars) unless stated otherwise
10. If you do not know something, say so and share contact details

User Question: {user_message}

Provide a helpful response based on the information above."""

        ai_response = _call_gemini(system_prompt)
        if ai_response:
            return Response({
                'response': ai_response,
                'source': 'gemini'
            })

        return Response({
            'response': get_fallback_response(user_message, db_context),
            'source': 'fallback'
        })

    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        return Response({
            'response': get_fallback_response(request.data.get('message', ''), get_database_context()),
            'source': 'fallback'
        }, status=status.HTTP_200_OK)


def get_fallback_response(message, db_context=None):
    """Fallback rule-based responses when AI is not available"""
    message_lower = (message or '').lower()
    company = (db_context or {}).get('company') or _company_info()
    packages = (db_context or {}).get('packages') or []

    contact_block = (
        f"📞 Phone: {company['phone']}\n"
        f"📧 Email: {company['email']}\n"
        f"💬 WhatsApp: {company['whatsapp']}\n"
        f"📍 Address: {company['address']}"
    )

    if any(word in message_lower for word in ['hello', 'hi', 'assalam', 'salam', 'hey']):
        return (
            "Assalamu Alaikum! 👋 Welcome to TM Fouzy Travel & Tours. "
            "How can I assist you with your Umrah or Hajj journey today?"
        )

    if any(word in message_lower for word in ['package', 'umrah', 'hajj', 'ziarah', 'tour']):
        if packages:
            lines = ["Here are some of our current packages:\n"]
            for pkg in packages[:5]:
                price = f"from ${pkg['price_from']:.0f}" if pkg.get('price_from') else "price on request"
                lines.append(
                    f"• {pkg['name']} — {pkg.get('duration', '')} — "
                    f"{pkg.get('travel_date', 'TBA')} — {price}"
                )
            lines.append("\nWould you like details on a specific package? You can also browse packages on our website.")
            return "\n".join(lines)
        return (
            "We offer Umrah, Hajj, and Ziarah packages with accommodation, transport, and visa assistance. "
            f"Browse packages on our website or contact us:\n{contact_block}"
        )

    if any(word in message_lower for word in ['price', 'cost', 'how much', 'rate']):
        priced = [p for p in packages if p.get('price_from')]
        if priced:
            cheapest = min(priced, key=lambda p: p['price_from'])
            return (
                f"Our packages currently start from ${cheapest['price_from']:.0f} per person "
                f"({cheapest['name']}). Prices vary by room type, travel dates, and duration.\n\n"
                f"For a personalised quote:\n{contact_block}"
            )
        return (
            "Prices vary by package, room sharing, and travel dates. "
            f"Contact us for detailed pricing:\n{contact_block}"
        )

    if any(word in message_lower for word in ['contact', 'phone', 'email', 'whatsapp', 'address']):
        return f"Contact Us:\n{contact_block}"

    if any(word in message_lower for word in ['book', 'booking', 'reserve']):
        return (
            "To book a package:\n"
            "1. Browse our packages on the website\n"
            "2. Select your preferred package\n"
            "3. Choose room type and add passengers\n"
            "4. Complete payment online\n\n"
            f"Need help? Contact us:\n{contact_block}"
        )

    if any(word in message_lower for word in ['payment', 'pay', 'paynow', 'deposit']):
        return (
            "We accept PayNow, Credit Card, Bank Transfer, and PayPal. "
            "A minimum deposit is required to confirm your booking; the balance can be paid later.\n\n"
            f"Questions about payment?\n{contact_block}"
        )

    return (
        "Thank you for your message! For detailed assistance, please contact us:\n"
        f"{contact_block}\n\n"
        "You can also ask me about packages, prices, booking, or payment options."
    )
