import os
import django
from datetime import date, datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Customer, Package, Booking, BookingRoom, Passenger

# Get customer
customer = Customer.objects.filter(email='ibrar@gmail.com').first()
if not customer:
    print("Customer not found!")
    exit()

print(f"Customer found: {customer.email}")

# Check existing bookings
existing_bookings = Booking.objects.filter(customer=customer)
print(f"Existing bookings: {existing_bookings.count()}")
for b in existing_bookings:
    print(f"  - {b.booking_number}: {b.package.name if b.package else 'No package'} - Status: {b.status}")

# Get an active package
package = Package.objects.filter(is_active=True).first()
if not package:
    print("No active packages found!")
    exit()

print(f"\nCreating booking for package: {package.name}")

# Create booking
booking = Booking.objects.create(
    customer=customer,
    package=package,
    booking_number=f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
    status='confirmed',
    total_amount=5000.00,
    paid_amount=1000.00,
    balance_amount=4000.00,
    contact_name=f"{customer.user.first_name} {customer.user.last_name}" if customer.user else "Ibrar",
    contact_phone=customer.phone,
    contact_email=customer.email,
    contact_address=customer.address,
    contact_postal=customer.postal_code,
    emergency_name="Emergency Contact",
    emergency_phone="+92 311 0000000",
    emergency_relationship="Family",
    special_requests="Test booking from mobile app",
    remarks="Created for mobile app testing"
)

print(f"Booking created: {booking.booking_number}")

# Create a room
room = BookingRoom.objects.create(
    booking=booking,
    room_number=1,
    sharing_type='double',
    price_per_person=2500.00,
    num_adults=2,
    num_children=0,
    num_infants=0,
    subtotal=5000.00
)

print(f"Room created: Room {room.room_number}")

# Create passengers
passenger1 = Passenger.objects.create(
    booking_room=room,
    passenger_type='adult',
    full_name='Ibrar Ahmed',
    phone=customer.phone,
    date_of_birth=date(1990, 1, 1),
    gender='male',
    passport_number='AB1234567',
    passport_expiry=date(2028, 12, 31),
    passport_issue_date=date(2023, 1, 1)
)

passenger2 = Passenger.objects.create(
    booking_room=room,
    passenger_type='adult',
    full_name='Sara Ahmed',
    phone=customer.phone,
    date_of_birth=date(1992, 5, 15),
    gender='female',
    passport_number='CD7890123',
    passport_expiry=date(2029, 6, 30),
    passport_issue_date=date(2024, 1, 1)
)

print(f"Passengers created: {passenger1.full_name}, {passenger2.full_name}")

print("\n✅ Booking created successfully!")
print(f"Booking Number: {booking.booking_number}")
print(f"Package: {package.name}")
print(f"Travel Date: {package.travel_date}")
print(f"Status: {booking.status}")
print(f"Total Amount: ${booking.total_amount}")
print(f"Paid Amount: ${booking.paid_amount}")
print(f"Balance: ${booking.balance_amount}")
