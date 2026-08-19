#!/usr/bin/env python
"""
TM FOUZY PACKAGES - ADD SCRIPT
Run this in backend directory: python add_packages.py
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Package, RoomSharingPrice, Category

def add_packages():
    print("=" * 60)
    print("TM FOUZY - Adding Packages")
    print("=" * 60)
    
    # Get categories
    umrah_cat = Category.objects.filter(category_type='umrah').first()
    ziarah_cat = Category.objects.filter(category_type='ziarah').first()
    
    if not umrah_cat or not ziarah_cat:
        print("❌ Error: Categories not found. Create Umrah and Ziarah categories first.")
        return
    
    packages_data = [
        # 1. Ramadhan Awal
        {
            'name': 'Umrah Ramadhan - Awal Ramadhan Package',
            'slug': 'umrah-ramadhan-awal-2025',
            'category': umrah_cat,
            'short_description': 'Ibadah yang lebih bermakna di bulan yang mulia - Awal Ramadhan 4-15 Feb 2025',
            'description': 'Paket Umrah Ramadhan di awal bulan suci dengan hotel premium dan full board meal.',
            'travel_date': '2025-02-04',
            'return_date': '2025-02-15',
            'duration_days': 12,
            'duration_nights': 11,
            'location': 'Makkah, Madinah',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 50,
            'min_deposit_amount': 1000,
            'hotel_name': 'Rayhaan by Rotana (Makkah), Dallah Taibah Hotel (Madinah)',
            'hotel_star_rating': 5,
            'hotel_country': 'Saudi Arabia',
            'inclusions': 'Tiket Penerbangan, Penginapan Hotel, Makan 3 Kali Sehari (Full Board), 3x Umrah Guided, Ziarah di Makkah & Madinah, Mutawwif Berpengalaman, Visa & Insurans',
            'exclusions': 'Shopping expenses, Personal expenses',
            'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set',
            'room_prices': [
                {'sharing_type': 'double', 'price': 4990},
                {'sharing_type': 'triple', 'price': 4790},
                {'sharing_type': 'quad', 'price': 4490},
            ]
        },
        # 2. Ramadhan Akhir
        {
            'name': 'Umrah Ramadhan - Akhir Ramadhan Package',
            'slug': 'umrah-ramadhan-akhir-2025',
            'category': umrah_cat,
            'short_description': 'Ibadah yang lebih bermakna di bulan yang mulia - Akhir Ramadhan 27 Feb - 12 Mar 2025',
            'description': 'Paket Umrah Ramadhan di akhir bulan suci dengan hotel premium Azka Al-Maqam dan Dallah Taibah.',
            'travel_date': '2025-02-27',
            'return_date': '2025-03-12',
            'duration_days': 14,
            'duration_nights': 13,
            'location': 'Makkah, Madinah',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 50,
            'min_deposit_amount': 1500,
            'hotel_name': 'Azka Al-Maqam (Makkah), Dallah Taibah Hotel (Madinah)',
            'hotel_star_rating': 5,
            'hotel_country': 'Saudi Arabia',
            'inclusions': 'Tiket Penerbangan, Penginapan Hotel, Makan 3 Kali Sehari (Full Board), 3x Umrah Guided, Ziarah di Makkah & Madinah, Mutawwif Berpengalaman, Visa & Insurans',
            'exclusions': 'Shopping expenses, Personal expenses',
            'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set',
            'room_prices': [
                {'sharing_type': 'double', 'price': 7890},
                {'sharing_type': 'triple', 'price': 6690},
                {'sharing_type': 'quad', 'price': 5690},
            ]
        },
        # 3. December Package 1
        {
            'name': 'Umrah End Year Package - December 1-11',
            'slug': 'umrah-december-1-11-2026',
            'category': umrah_cat,
            'short_description': 'End of Year Umrah Package Dec 2026 - Dallah Taibah Hotel Madinah',
            'description': 'Umrah package with premium hotels: Dallah Taibah (Madinah) and Hotel Rayhaan by Rotana (Makkah)',
            'travel_date': '2026-12-01',
            'return_date': '2026-12-11',
            'duration_days': 11,
            'duration_nights': 10,
            'location': 'Makkah, Madinah',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 50,
            'min_deposit_amount': 1000,
            'hotel_name': 'Rayhaan by Rotana (Makkah), Dallah Taibah Hotel (Madinah)',
            'hotel_star_rating': 5,
            'hotel_country': 'Saudi Arabia',
            'inclusions': 'Economy Round Trip, Guided Journey, Tours & Transfers, 5-Star Hotel, Full Board Meal, Visa Expenses, Departure Accessories, High Speed Train',
            'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set, 2km from Zam Zam 2 liters',
            'room_prices': [
                {'sharing_type': 'double', 'price': 4990},
                {'sharing_type': 'triple', 'price': 4690},
                {'sharing_type': 'quad', 'price': 4390},
                {'sharing_type': 'child_with_bed', 'price': 3990},
                {'sharing_type': 'child_no_bed', 'price': 2990},
            ]
        },
        # 4. December Package 2
        {
            'name': 'Umrah End Year Package - December 15-25',
            'slug': 'umrah-december-15-25-2026',
            'category': umrah_cat,
            'short_description': 'End of Year Umrah Package Dec 2026 - Premium Hotels',
            'description': 'Umrah package with premium hotels: Dallah Taibah (Madinah) and Hotel Rayhaan by Rotana (Makkah)',
            'travel_date': '2026-12-15',
            'return_date': '2026-12-25',
            'duration_days': 11,
            'duration_nights': 10,
            'location': 'Makkah, Madinah',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 50,
            'min_deposit_amount': 1000,
            'hotel_name': 'Rayhaan by Rotana (Makkah), Dallah Taibah Hotel (Madinah)',
            'hotel_star_rating': 5,
            'hotel_country': 'Saudi Arabia',
            'inclusions': 'Economy Round Trip, Guided Journey, Tours & Transfers, 5-Star Hotel, Full Board Meal, Visa Expenses, Departure Accessories, High Speed Train',
            'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set, 2km from Zam Zam 2 liters',
            'room_prices': [
                {'sharing_type': 'double', 'price': 5390},
                {'sharing_type': 'triple', 'price': 5090},
                {'sharing_type': 'quad', 'price': 4790},
                {'sharing_type': 'child_with_bed', 'price': 4390},
                {'sharing_type': 'child_no_bed', 'price': 2990},
            ]
        },
        # 5. Baitul Maqdis 9 Days
        {
            'name': 'The Sacred Journey - Baitul Maqdis (9 Days)',
            'slug': 'baitul-maqdis-9-days-jan-2026',
            'category': ziarah_cat,
            'short_description': 'Amman, Petra, Baitul Maqdis - 9 Days Sacred Journey',
            'description': 'Jelajah Bumi Anbiya - Visit Petra, Baitul Maqdis (Jerusalem), and Hebron with Ustaz TM Fauwaz as guide',
            'travel_date': '2026-01-01',
            'return_date': '2026-01-09',
            'duration_days': 9,
            'duration_nights': 8,
            'location': 'Amman, Petra, Baitul Maqdis, Hebron',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 40,
            'min_deposit_amount': 1000,
            'hotel_name': 'Grand Court Hotel (Jerusalem), Regency Palace Hotel (Amman)',
            'hotel_star_rating': 5,
            'hotel_country': 'Jordan, Palestine',
            'inclusions': 'Economy Round Trip, Guided Journey, Tours & Transfers, 5-Star Hotel, Full Board Meal, Visa Expenses, Departure Accessories',
            'complimentary_items': 'Travel accessories',
            'itinerary': [
                {"day": 1, "title": "Amman Arrival", "description": "Arrival at Amman, Jordan"},
                {"day": 2, "title": "Petra Tour", "description": "Full day tour of Petra ancient city"},
                {"day": 3, "title": "Baitul Maqdis", "description": "Visit Al-Aqsa Mosque and Dome of the Rock"},
                {"day": 4, "title": "Jerusalem Old City", "description": "Explore Jerusalem old city"},
                {"day": 5, "title": "Hebron", "description": "Visit Prophet Ibrahim tomb"}
            ],
            'room_prices': [
                {'sharing_type': 'double', 'price': 4290},
                {'sharing_type': 'child_with_bed', 'price': 3690},
                {'sharing_type': 'child_no_bed', 'price': 3390},
            ]
        },
        # 6. Baitul Maqdis + Umrah 15 Days
        {
            'name': 'The Sacred Journey - Umrah + Baitul Maqdis (15 Days)',
            'slug': 'umrah-baitul-maqdis-15-days-2025',
            'category': ziarah_cat,
            'short_description': 'Amman, Petra, Baitul Maqdis + Umrah - 15 Days Complete Journey',
            'description': 'Complete package combining Baitul Maqdis tour with Umrah, guided by Ustaz TM Fauwaz',
            'travel_date': '2025-12-26',
            'return_date': '2026-01-09',
            'duration_days': 15,
            'duration_nights': 14,
            'location': 'Amman, Petra, Baitul Maqdis, Makkah, Madinah',
            'is_featured': True,
            'is_active': True,
            'max_capacity': 40,
            'min_deposit_amount': 1500,
            'hotel_name': 'Grand Court Hotel (Jerusalem), Al Safwah Hotel Tower 3 (Makkah), Dallah Taibah Hotel (Madinah)',
            'hotel_star_rating': 5,
            'hotel_country': 'Jordan, Palestine, Saudi Arabia',
            'inclusions': 'Economy Round Trip, Guided Journey, Tours & Transfers, 5-Star Hotel, Full Board Meal, Visa Expenses, Departure Accessories, High Speed Train',
            'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set',
            'itinerary': [
                {"day": 1, "title": "Amman Arrival", "description": "Arrival at Amman, Jordan"},
                {"day": 2, "title": "Petra Tour", "description": "Full day tour of Petra"},
                {"day": 3, "title": "Baitul Maqdis", "description": "Visit Al-Aqsa Mosque"},
                {"day": 8, "title": "Makkah", "description": "Arrive in Makkah, perform Umrah"},
                {"day": 12, "title": "Madinah", "description": "Visit Masjid Nabawi"}
            ],
            'room_prices': [
                {'sharing_type': 'double', 'price': 6390},
                {'sharing_type': 'child_with_bed', 'price': 5090},
                {'sharing_type': 'child_no_bed', 'price': 4090},
            ]
        },
    ]
    
    created_count = 0
    skipped_count = 0
    
    for pkg_data in packages_data:
        slug = pkg_data['slug']
        
        # Check if exists
        if Package.objects.filter(slug=slug).exists():
            print(f"⏭️  Skipped: {pkg_data['name']} (already exists)")
            skipped_count += 1
            continue
        
        # Extract room prices
        room_prices = pkg_data.pop('room_prices')
        
        # Create package
        try:
            package = Package.objects.create(**pkg_data)
            
            # Add room prices
            for room in room_prices:
                RoomSharingPrice.objects.create(
                    package=package,
                    sharing_type=room['sharing_type'],
                    price=room['price'],
                    available=True,
                    max_capacity=pkg_data['max_capacity']
                )
            
            print(f"✅ Created: {package.name}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating {pkg_data['name']}: {e}")
    
    print("=" * 60)
    print(f"✅ Created: {created_count} packages")
    print(f"⏭️  Skipped: {skipped_count} packages (already exist)")
    print("=" * 60)

if __name__ == '__main__':
    add_packages()
