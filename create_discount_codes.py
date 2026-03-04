import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import DiscountCode
from django.utils import timezone

# Create sample discount codes
discount_codes = [
    {
        'code': 'WELCOME10',
        'discount_type': 'percentage',
        'discount_value': 10,
        'min_purchase_amount': 50,
        'max_discount_amount': 100,
        'usage_limit': None,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=365),
        'is_active': True
    },
    {
        'code': 'SAVE20',
        'discount_type': 'fixed',
        'discount_value': 20,
        'min_purchase_amount': 100,
        'max_discount_amount': None,
        'usage_limit': 100,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=90),
        'is_active': True
    },
    {
        'code': 'SPECIAL50',
        'discount_type': 'fixed',
        'discount_value': 50,
        'min_purchase_amount': 200,
        'max_discount_amount': None,
        'usage_limit': 50,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=30),
        'is_active': True
    }
]

for code_data in discount_codes:
    code, created = DiscountCode.objects.get_or_create(
        code=code_data['code'],
        defaults=code_data
    )
    if created:
        print(f"✓ Created discount code: {code.code}")
    else:
        print(f"- Discount code already exists: {code.code}")

print("\n✓ Discount codes setup complete!")
print("\nAvailable discount codes:")
print("1. WELCOME10 - 10% off (min $50, max discount $100)")
print("2. SAVE20 - $20 off (min $100)")
print("3. SPECIAL50 - $50 off (min $200)")
