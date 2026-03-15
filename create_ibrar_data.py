"""
Run this on PythonAnywhere:
  cd ~/umrahagencybackend && python create_ibrar_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Customer, Category, Package, Booking, BookingRoom, Passenger, Payment
from decimal import Decimal
from datetime import date
import random, string

def make_booking_number():
    return 'BK' + ''.join(random.choices(string.digits, k=6))

def make_payment_number():
    return 'PAY' + ''.join(random.choices(string.digits, k=6))

email = 'ibrar@gmail.com'

# ── 1. Find existing user ───────────────────────────────────────
try:
    user = User.objects.get(username=email)
    print(f'✅ User found: {user.username} (id={user.id})')
except User.DoesNotExist:
    print(f'❌ User {email} not found. Please register first.')
    exit(1)

# ── 2. Get or create Customer profile ──────────────────────────
customer, created = Customer.objects.get_or_create(
    email=email,
    defaults={
        'user': user,
        'phone': '+65 9123 4567',
        'address': '123 Orchard Road',
        'city': 'Singapore',
        'country': 'Singapore',
        'postal_code': '238858',
    }
)
if not customer.user:
    customer.user = user
    customer.save()
print(f'✅ Customer profile ready ({"created" if created else "existing"})')

# ── 3. Get or create Category ───────────────────────────────────
category, _ = Category.objects.get_or_create(
    slug='umrah-packages',
    defaults={
        'name': 'Umrah Packages',
        'category_type': 'umrah',
        'description': 'Premium Umrah packages from Singapore',
        'is_active': True,
        'order': 1,
    }
)
print(f'✅ Category ready: {category.name}')

# ── 4. Get or create Package ────────────────────────────────────
package, _ = Package.objects.get_or_create(
    slug='ramadan-umrah-2026',
    defaults={
        'category': category,
        'name': 'Ramadan Umrah Package 2026',
        'description': 'A blessed journey to Makkah and Madinah during the holy month of Ramadan. Includes 5-star hotel accommodation, guided tours, and all meals.',
        'short_description': '14 Days Umrah during Ramadan with 5-star hotels',
        'travel_date': date(2026, 3, 20),
        'return_date': date(2026, 4, 3),
        'duration_days': 14,
        'duration_nights': 13,
        'location': 'Makkah & Madinah, Saudi Arabia',
        'inclusions': 'Return flights\n5-star hotel in Makkah (7 nights)\n5-star hotel in Madinah (6 nights)\nAll meals\nAirport transfers\nGuided Ziyarah tours\nUmrah visa\nTravel insurance',
        'exclusions': 'Personal expenses\nOptional tours\nLaundry',
        'complimentary_items': 'Prayer mat\nZamzam bottle (5L)\nIhram set\nUmrah guide book',
        'featured_image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=800',
        'is_featured': True,
        'is_active': True,
        'min_deposit_amount': Decimal('500.00'),
        'min_deposit_percentage': Decimal('20.00'),
        'hotel_name': 'Makkah Clock Royal Tower',
        'hotel_star_rating': 5,
        'hotel_country': 'Saudi Arabia',
        'max_capacity': 40,
    }
)
print(f'✅ Package ready: {package.name}')

# ── 5. Create Booking ───────────────────────────────────────────
existing = Booking.objects.filter(customer=customer).first()
if existing:
    booking = existing
    print(f'ℹ️  Booking already exists: {booking.booking_number}')
else:
    booking = Booking.objects.create(
        customer=customer,
        package=package,
        booking_number=make_booking_number(),
        status='confirmed',
        total_amount=Decimal('3800.00'),
        paid_amount=Decimal('1500.00'),
        balance_amount=Decimal('2300.00'),
        contact_name='Ibrar Ahmed',
        contact_phone='+65 9123 4567',
        contact_email=email,
        contact_address='123 Orchard Road',
        contact_unit='#05-12',
        contact_postal='238858',
        emergency_name='Sara Ahmed',
        emergency_phone='+65 9876 5432',
        emergency_relationship='Spouse',
        special_requests='Wheelchair assistance needed at airport',
        remarks='VIP customer',
    )
    print(f'✅ Booking created: {booking.booking_number}')

# ── 6. Create Room + Passengers ─────────────────────────────────
if not booking.rooms.exists():
    room = BookingRoom.objects.create(
        booking=booking,
        room_number=1,
        sharing_type='double',
        price_per_person=Decimal('1900.00'),
        num_adults=2,
        num_children=0,
        num_infants=0,
        subtotal=Decimal('3800.00'),
    )
    Passenger.objects.create(
        booking_room=room,
        passenger_type='adult',
        full_name='Ibrar Ahmed',
        phone='+65 9123 4567',
        date_of_birth=date(1985, 6, 15),
        gender='male',
        passport_number='A12345678',
        passport_expiry=date(2030, 6, 14),
        passport_issue_date=date(2020, 6, 15),
    )
    Passenger.objects.create(
        booking_room=room,
        passenger_type='adult',
        full_name='Sara Ahmed',
        phone='+65 9876 5432',
        date_of_birth=date(1988, 9, 22),
        gender='female',
        passport_number='B98765432',
        passport_expiry=date(2029, 9, 21),
        passport_issue_date=date(2019, 9, 22),
    )
    print(f'✅ Room + 2 passengers created')
else:
    print(f'ℹ️  Room already exists')

# ── 7. Create Payment ───────────────────────────────────────────
if not booking.payments.exists():
    Payment.objects.create(
        booking=booking,
        customer=customer,
        payment_number=make_payment_number(),
        amount=Decimal('1500.00'),
        payment_method='bank_transfer',
        status='completed',
        transaction_id='TXN-SG-2026-001',
        notes='Initial deposit via PayNow',
    )
    print(f'✅ Payment created: $1500.00')
else:
    print(f'ℹ️  Payment already exists')

print()
print('=' * 50)
print(f'✅ DONE!')
print(f'   Booking : {booking.booking_number}')
print(f'   Status  : {booking.status}')
print(f'   Package : {package.name}')
print(f'   Total   : ${booking.total_amount}')
print(f'   Paid    : ${booking.paid_amount}')
print(f'   Balance : ${booking.balance_amount}')
print('=' * 50)
