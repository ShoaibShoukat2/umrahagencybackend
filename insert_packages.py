"""
Run this script from the backend folder:
  python insert_packages.py

It will:
1. Create/find the Umrah category
2. Insert all 25 packages (2 Ramadhan + 23 Umrah 2026)
3. Insert room prices for each package
"""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Category, Package, RoomSharingPrice
from decimal import Decimal
import re

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def get_or_create_umrah_category():
    cat, created = Category.objects.get_or_create(
        slug='umrah-packages',
        defaults={
            'name': 'Umrah Packages',
            'category_type': 'umrah',
            'description': 'Premium Umrah packages from Singapore with guided rituals, Haram-side hotels, and full board meals.',
            'is_active': True,
            'order': 1,
        }
    )
    if created:
        print(f'  ✅ Created category: {cat.name}')
    else:
        print(f'  ✅ Using existing category: {cat.name} (id={cat.id})')
    return cat

def make_inclusions():
    return """- Return Air Ticket
- Saudi Umrah Visa
- 5-Star Hotel Accommodation
- Full Board Meals (Breakfast, Lunch & Dinner)
- 3x Guided Umrah
- Ziarah in Makkah & Madinah
- Experienced Mutawwif & Tour Guide
- Haramain High Speed Train
- Tours & Transfers
- Receiver Device (Tour Guide Audio System)"""

def make_complimentary():
    return """Cabin Trolley Bag, Ihram for Men, Mini Telekung for Ladies, Doa Booklet, Zamzam 5 Liter, Prayer Mat, Umbrella, Tawaf Rosary, Sling Bag"""

def make_ramadhan_inclusions():
    return """- Return Air Ticket
- Saudi Umrah Visa
- Hotel Accommodation
- Full Board Meals — Sahur & Iftar (3 meals daily)
- 3x Guided Umrah
- Ziarah in Makkah & Madinah
- Experienced Mutawwif & Tour Guide"""

def create_package(cat, name, travel_date, return_date, days, nights,
                   location, hotel_name, short_desc, inclusions, complimentary,
                   min_deposit=500, featured=False):
    pkg_slug = slug(name)
    # avoid duplicate slugs
    base = pkg_slug
    counter = 1
    while Package.objects.filter(slug=pkg_slug).exists():
        pkg_slug = f'{base}-{counter}'
        counter += 1

    pkg = Package.objects.create(
        category=cat,
        name=name,
        slug=pkg_slug,
        short_description=short_desc,
        description=short_desc,
        travel_date=travel_date,
        return_date=return_date,
        duration_days=days,
        duration_nights=nights,
        location=location,
        hotel_name=hotel_name,
        hotel_star_rating=5,
        hotel_country='Saudi Arabia',
        inclusions=inclusions,
        complimentary_items=complimentary,
        min_deposit_amount=Decimal(str(min_deposit)),
        min_deposit_percentage=Decimal('20'),
        child_no_bed_price_percentage=Decimal('100'),
        infant_price_percentage=Decimal('25'),
        max_capacity=50,
        is_active=True,
        is_featured=featured,
        itinerary=[],
    )
    return pkg

def add_prices(pkg, double=None, triple=None, quad=None,
               child_with_bed=None, child_no_bed=None, single=None):
    mapping = {
        'double':         double,
        'triple':         triple,
        'quad':           quad,
        'child_with_bed': child_with_bed,
        'child_no_bed':   child_no_bed,
        'single':         single,
    }
    for sharing_type, price in mapping.items():
        if price is not None:
            RoomSharingPrice.objects.get_or_create(
                package=pkg,
                sharing_type=sharing_type,
                defaults={'price': Decimal(str(price)), 'available': True, 'max_capacity': 50}
            )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
cat = get_or_create_umrah_category()

# ─── RAMADHAN PACKAGES ───────────────────────────────────────────────────────

print('\n📦 Inserting Ramadhan packages...')

# Package R1 — Awal Ramadhan
r1 = create_package(
    cat=cat,
    name='Awal Ramadhan — 4 Feb 2025',
    travel_date='2025-02-04',
    return_date='2025-02-15',
    days=12, nights=11,
    location='Makkah & Madinah',
    hotel_name='Rayhaan by Rotana, Makkah (50m) + Dallah Taibah, Madinah (200m)',
    short_desc='Umrah Ramadhan Awal — Rayhaan by Rotana 50m from Masjidil Haram (5N) + Dallah Taibah 200m from Masjid Nabawi (5N). Full Board Meals Sahur & Iftar.',
    inclusions=make_ramadhan_inclusions(),
    complimentary='',
    min_deposit=500,
    featured=True,
)
add_prices(r1, double=4990, triple=4790, quad=4490)
print(f'  ✅ {r1.name}')

# Package R2 — Akhir Ramadhan
r2 = create_package(
    cat=cat,
    name='Akhir Ramadhan — 27 Feb 2025',
    travel_date='2025-02-27',
    return_date='2025-03-12',
    days=14, nights=13,
    location='Makkah & Madinah',
    hotel_name='Azka Al-Maqam, Makkah (200m) + Dallah Taibah, Madinah (200m)',
    short_desc='Umrah Ramadhan Akhir — Azka Al-Maqam 200m from Masjidil Haram (10N) + Dallah Taibah 200m from Masjid Nabawi (3N). Full Board Sahur & Iftar.',
    inclusions=make_ramadhan_inclusions(),
    complimentary='',
    min_deposit=500,
    featured=True,
)
add_prices(r2, double=7890, triple=6690, quad=5690)
print(f'  ✅ {r2.name}')

# ─── UMRAH 2026 PACKAGES ─────────────────────────────────────────────────────

print('\n📦 Inserting Umrah 2026 packages...')

inc_2026 = make_inclusions()
comp_2026 = make_complimentary()

packages_2026 = [
    # (name, travel_date, return_date, days, nights, airline, arrival, madinah_hotel, double, triple, quad, child_with_bed, child_no_bed)
    ('Umrah 19 Sep – 30 Sep 2026 (SV)',  '2026-09-19','2026-09-30',12,11,'SV','MAD','Al Harithia (90m)',  4290,4090,3890,3690,2590),
    ('Umrah 26 Sep – 7 Oct 2026 (QR)',   '2026-09-26','2026-10-07',12,11,'QR','MAD','Al Harithia (90m)',  4290,4090,3890,3690,2590),
    ('Umrah 3 Oct – 14 Oct 2026 (SV)',   '2026-10-03','2026-10-14',12,11,'SV','MAD','The Venue Al Harithia (90m)', 4490,4190,3990,3790,2590),
    ('Umrah 24 Oct – 4 Nov 2026 (SV)',   '2026-10-24','2026-11-04',12,11,'SV','MAD','Dallah Taibah (90m)', 4690,4390,4190,3790,2590),
    ('Umrah 10 Nov – 20 Nov 2026 (SV)',  '2026-11-10','2026-11-20',11,10,'SV','MAD','Dallah Taibah (90m)', 4490,4290,4090,3690,2690),
    ('Umrah 18 Nov – 30 Nov 2026 (QR)',  '2026-11-18','2026-11-30',13,12,'QR','MAD','Dallah Taibah (90m)', 5290,4990,4690,4290,3290),
    ('Umrah 21 Nov – 2 Dec 2026 (SV)',   '2026-11-21','2026-12-02',12,11,'SV','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 24 Nov – 4 Dec 2026 (SV)',   '2026-11-24','2026-12-04',11,10,'SV','MAK','Dallah Taibah (90m)', 4990,4690,4390,3990,2990),
    ('Umrah 25 Nov – 6 Dec 2026 (QR)',   '2026-11-25','2026-12-06',12,11,'QR','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 28 Nov – 9 Dec 2026 (SV)',   '2026-11-28','2026-12-09',12,11,'SV','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 1 Dec – 11 Dec 2026 (SV)',   '2026-12-01','2026-12-11',11,10,'SV','MAK','Dallah Taibah (90m)', 4990,4690,4390,3990,2990),
    ('Umrah 2 Dec – 13 Dec 2026 (QR)',   '2026-12-02','2026-12-13',12,11,'QR','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 5 Dec – 14 Dec 2026 (SV)',   '2026-12-05','2026-12-14',10,9, 'SV','MAD','Dallah Taibah (90m)', 4790,4490,4190,3790,2790),
    ('Umrah 5 Dec – 16 Dec 2026 (SV)',   '2026-12-05','2026-12-16',12,11,'SV','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 8 Dec – 18 Dec 2026 (SV)',   '2026-12-08','2026-12-18',11,10,'SV','MAK','Dallah Taibah (90m)', 4990,4690,4390,3990,2990),
    ('Umrah 10 Dec – 21 Dec 2026 (QR)',  '2026-12-10','2026-12-21',12,11,'QR','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 12 Dec – 23 Dec 2026 (SV)',  '2026-12-12','2026-12-23',12,11,'SV','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 12 Dec – 23 Dec 2026 (QR)',  '2026-12-12','2026-12-23',12,11,'QR','MAD','Dallah Taibah (90m)', 5190,4890,4590,4190,3190),
    ('Umrah 15 Dec – 25 Dec 2026 (SV)',  '2026-12-15','2026-12-25',11,10,'SV','MAK','Dallah Taibah (90m)', 5390,5090,4790,4390,2990),
    ('Umrah 16 Dec – 27 Dec 2026 (QR)',  '2026-12-16','2026-12-27',12,11,'QR','MAD','Dallah Taibah (90m)', 5490,5190,4890,4490,3190),
    ('Umrah 23 Dec – 1 Jan 2027 (QR)',   '2026-12-23','2027-01-01',10,9, 'QR','MAD','Dallah Taibah (90m)', 5390,5090,4790,4390,2790),
]

for (name, tdate, rdate, days, nights, airline, arrival, madinah_hotel,
     dbl, tri, quad, cwb, cnb) in packages_2026:

    arrival_city = 'Madinah' if arrival == 'MAD' else 'Makkah'
    hotel_str = f'Al-Marwa Rayhaan by Rotana, Makkah (50m) + {madinah_hotel}, Madinah'
    short = (f'{days}-day Umrah package via {airline}. '
             f'Fly to {arrival_city} first. '
             f'Makkah: Al-Marwa Rayhaan by Rotana (50m from Haram). '
             f'Madinah: {madinah_hotel} from Masjid Nabawi. '
             f'Full Board. 3x Guided Umrah. Visa included. Haramain Train included.')

    pkg = create_package(
        cat=cat,
        name=name,
        travel_date=tdate,
        return_date=rdate,
        days=days,
        nights=nights,
        location='Makkah & Madinah',
        hotel_name=hotel_str,
        short_desc=short,
        inclusions=inc_2026,
        complimentary=comp_2026,
        min_deposit=500,
        featured=False,
    )
    add_prices(pkg, double=dbl, triple=tri, quad=quad,
               child_with_bed=cwb, child_no_bed=cnb)
    print(f'  ✅ {pkg.name}')

print('\n🎉 Done! All packages inserted successfully.')
print(f'   Total packages created: {2 + len(packages_2026)}')
