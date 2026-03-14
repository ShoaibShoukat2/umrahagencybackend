"""
Sample Data Script for TM Fouzy Travel & Tours
Run on PythonAnywhere: python add_sample_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category, Package, RoomSharingPrice, TravelItem, Tag
from datetime import date

print("Adding sample data...")

# ==================== CATEGORIES ====================
cats = [
    {'name': 'Umrah Packages', 'slug': 'umrah-packages', 'category_type': 'umrah',
     'description': 'Complete Umrah packages with hotel and transport',
     'image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=800', 'order': 1},
    {'name': 'Hajj Packages', 'slug': 'hajj-packages', 'category_type': 'hajj',
     'description': 'Full Hajj packages with all inclusive services',
     'image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=800', 'order': 2},
    {'name': 'Ziarah Tours', 'slug': 'ziarah-tours', 'category_type': 'ziarah',
     'description': 'Historical and religious site tours',
     'image': 'https://images.unsplash.com/photo-1519817650390-64a93db51149?w=800', 'order': 3},
    {'name': 'Holiday Packages', 'slug': 'holiday-packages', 'category_type': 'holiday',
     'description': 'Relaxing holiday packages for families',
     'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800', 'order': 4},
    {'name': 'Travel Items', 'slug': 'travel-items', 'category_type': 'item',
     'description': 'Essential travel accessories and items',
     'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800', 'order': 5},
]

created_cats = {}
for c in cats:
    obj, created = Category.objects.get_or_create(slug=c['slug'], defaults=c)
    created_cats[c['slug']] = obj
    print(f"  Category: {obj.name} ({'created' if created else 'exists'})")

# ==================== PACKAGES ====================
packages = [
    {
        'category': created_cats['umrah-packages'],
        'name': 'Umrah Economy Package 2026',
        'slug': 'umrah-economy-2026',
        'short_description': 'Affordable Umrah package with 4-star hotel near Haram',
        'description': 'Experience the spiritual journey of Umrah with our economy package. Includes 4-star hotel accommodation, airport transfers, and guided tours.',
        'travel_date': date(2026, 5, 1),
        'return_date': date(2026, 5, 15),
        'duration_days': 15, 'duration_nights': 14,
        'location': 'Makkah & Madinah, Saudi Arabia',
        'inclusions': 'Return airfare\n4-star hotel in Makkah (7 nights)\n4-star hotel in Madinah (5 nights)\nAirport transfers\nGuided Umrah assistance\nZamzam water',
        'exclusions': 'Personal expenses\nOptional tours\nTravel insurance',
        'featured_image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=800',
        'is_featured': True, 'is_active': True,
        'min_deposit_amount': 500, 'min_deposit_percentage': 20,
        'hotel_name': 'Makkah Clock Royal Tower', 'hotel_star_rating': 4,
        'hotel_country': 'Saudi Arabia',
        'hotel_image': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
        'max_capacity': 40,
    },
    {
        'category': created_cats['umrah-packages'],
        'name': 'Umrah Premium Package 2026',
        'slug': 'umrah-premium-2026',
        'short_description': 'Luxury Umrah experience with 5-star hotel steps from Haram',
        'description': 'Our premium Umrah package offers the finest experience with 5-star accommodation, private transfers, and personalized guidance throughout your journey.',
        'travel_date': date(2026, 6, 1),
        'return_date': date(2026, 6, 18),
        'duration_days': 18, 'duration_nights': 17,
        'location': 'Makkah & Madinah, Saudi Arabia',
        'inclusions': 'Business class airfare\n5-star hotel in Makkah (10 nights)\n5-star hotel in Madinah (5 nights)\nPrivate airport transfers\nPersonal Umrah guide\nZamzam water\nComplimentary prayer kit',
        'exclusions': 'Personal expenses\nTravel insurance',
        'featured_image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=800',
        'is_featured': True, 'is_active': True,
        'min_deposit_amount': 1000, 'min_deposit_percentage': 20,
        'hotel_name': 'Abraj Al-Bait Towers', 'hotel_star_rating': 5,
        'hotel_country': 'Saudi Arabia',
        'hotel_image': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
        'max_capacity': 30,
    },
    {
        'category': created_cats['hajj-packages'],
        'name': 'Hajj Standard Package 2026',
        'slug': 'hajj-standard-2026',
        'short_description': 'Complete Hajj package with all essential services included',
        'description': 'Perform the sacred Hajj with peace of mind. Our standard package covers all the essentials for a complete and spiritually fulfilling Hajj experience.',
        'travel_date': date(2026, 6, 10),
        'return_date': date(2026, 7, 5),
        'duration_days': 25, 'duration_nights': 24,
        'location': 'Makkah, Madinah & Mina, Saudi Arabia',
        'inclusions': 'Return airfare\n4-star hotel accommodation\nMina tent accommodation\nArafat & Muzdalifah arrangements\nAirport transfers\nGuided Hajj assistance\nMeals during Hajj days',
        'exclusions': 'Personal expenses\nOptional ziarah tours\nTravel insurance',
        'featured_image': 'https://images.unsplash.com/photo-1519817650390-64a93db51149?w=800',
        'is_featured': True, 'is_active': True,
        'min_deposit_amount': 2000, 'min_deposit_percentage': 30,
        'hotel_name': 'Hilton Makkah Convention Hotel', 'hotel_star_rating': 4,
        'hotel_country': 'Saudi Arabia',
        'hotel_image': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
        'max_capacity': 50,
    },
    {
        'category': created_cats['ziarah-tours'],
        'name': 'Madinah Ziarah Tour 2026',
        'slug': 'madinah-ziarah-2026',
        'short_description': 'Visit the holy sites of Madinah with expert guidance',
        'description': 'Explore the blessed city of Madinah and its historical Islamic sites with our expert guides. Visit Masjid Nabawi, Quba Mosque, and other significant locations.',
        'travel_date': date(2026, 7, 1),
        'return_date': date(2026, 7, 8),
        'duration_days': 8, 'duration_nights': 7,
        'location': 'Madinah, Saudi Arabia',
        'inclusions': 'Return airfare\n4-star hotel in Madinah\nGuided ziarah tours\nAirport transfers\nBreakfast daily',
        'exclusions': 'Lunch and dinner\nPersonal expenses\nTravel insurance',
        'featured_image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800',
        'is_featured': False, 'is_active': True,
        'min_deposit_amount': 300, 'min_deposit_percentage': 20,
        'hotel_name': 'Anwar Al Madinah Mövenpick', 'hotel_star_rating': 4,
        'hotel_country': 'Saudi Arabia',
        'hotel_image': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
        'max_capacity': 35,
    },
]

created_pkgs = {}
for p in packages:
    obj, created = Package.objects.get_or_create(slug=p['slug'], defaults=p)
    created_pkgs[p['slug']] = obj
    print(f"  Package: {obj.name} ({'created' if created else 'exists'})")

# ==================== ROOM PRICES ====================
room_prices = {
    'umrah-economy-2026': {'single': 3500, 'double': 2800, 'triple': 2500, 'quad': 2200},
    'umrah-premium-2026': {'single': 6500, 'double': 5500, 'triple': 5000, 'quad': 4500},
    'hajj-standard-2026': {'single': 12000, 'double': 10000, 'triple': 9000, 'quad': 8500},
    'madinah-ziarah-2026': {'single': 2500, 'double': 2000, 'triple': 1800, 'quad': 1600},
}

for slug, prices in room_prices.items():
    if slug in created_pkgs:
        pkg = created_pkgs[slug]
        for sharing_type, price in prices.items():
            obj, created = RoomSharingPrice.objects.get_or_create(
                package=pkg, sharing_type=sharing_type,
                defaults={'price': price, 'available': True, 'max_capacity': 50}
            )
            if created:
                print(f"  Room price: {pkg.name} - {sharing_type}: ${price}")

# ==================== TRAVEL ITEMS ====================
item_cat = created_cats['travel-items']
items = [
    {'name': 'Ihram Set (Men)', 'slug': 'ihram-set-men', 'category': item_cat,
     'description': 'Complete Ihram set for men including 2 white towels. High quality cotton material.',
     'price': 25.00, 'stock_quantity': 100, 'is_active': True,
     'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'},
    {'name': 'Prayer Mat', 'slug': 'prayer-mat', 'category': item_cat,
     'description': 'Portable travel prayer mat. Lightweight and easy to carry.',
     'price': 15.00, 'stock_quantity': 150, 'is_active': True,
     'image': 'https://images.unsplash.com/photo-1585036156171-384164a8c675?w=400'},
    {'name': 'Zamzam Bottle (5L)', 'slug': 'zamzam-bottle-5l', 'category': item_cat,
     'description': 'Premium Zamzam water bottle 5 liters. Sealed and certified.',
     'price': 20.00, 'stock_quantity': 200, 'is_active': True,
     'image': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400'},
    {'name': 'Travel Tasbih', 'slug': 'travel-tasbih', 'category': item_cat,
     'description': 'Digital tasbih counter. Easy to use with wrist strap.',
     'price': 12.00, 'stock_quantity': 80, 'is_active': True,
     'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'},
    {'name': 'Umrah Guide Book', 'slug': 'umrah-guide-book', 'category': item_cat,
     'description': 'Comprehensive Umrah guide with duas and step-by-step instructions.',
     'price': 18.00, 'stock_quantity': 60, 'is_active': True,
     'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'},
]

for item in items:
    obj, created = TravelItem.objects.get_or_create(slug=item['slug'], defaults=item)
    print(f"  Item: {obj.name} ({'created' if created else 'exists'})")

print("\nSample data added successfully!")
print(f"  Categories: {Category.objects.count()}")
print(f"  Packages: {Package.objects.count()}")
print(f"  Travel Items: {TravelItem.objects.count()}")
