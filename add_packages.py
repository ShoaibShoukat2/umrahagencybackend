#!/usr/bin/env python
"""
TM FOUZY PACKAGES - ADD/UPDATE SCRIPT
Run this in backend directory: python add_packages.py

This script:
- Creates packages if they don't exist
- UPDATES existing packages with latest data (including images)
- Downloads images from internet and saves to media folder
"""
import os
import sys
import django
import urllib.request
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from api.models import Package, RoomSharingPrice, Category
from backend.settings import MEDIA_ROOT

def download_image(url, filename):
    """Download image from URL and save to media folder, return relative path"""
    try:
        folder = os.path.dirname(filename)
        full_folder = os.path.join(MEDIA_ROOT, folder)
        os.makedirs(full_folder, exist_ok=True)

        full_path = os.path.join(MEDIA_ROOT, filename)

        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(full_path, 'wb') as f:
                f.write(response.read())

        print(f"    📸 Downloaded: {filename}")
        return filename
    except Exception as e:
        print(f"    ⚠️  Could not download image ({url[:60]}...): {e}")
        return ''

def set_package_image(package, field_name, image_path):
    """Set image field directly by path without re-downloading"""
    try:
        full_path = os.path.join(MEDIA_ROOT, image_path)
        if os.path.exists(full_path):
            setattr(package, field_name, image_path)
            return True
    except Exception as e:
        print(f"    ⚠️  Could not set {field_name}: {e}")
    return False

# ============================================================
# IMAGE SOURCES (using reliable image URLs)
# ============================================================
IMAGES = {
    # Package featured images - Umrah Makkah/Madinah images
    'ramadhan_awal': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Makkah_-_panoramio_%284%29.jpg/1200px-Makkah_-_panoramio_%284%29.jpg',
        'path': 'packages/ramadhan-awal-2025.jpg'
    },
    'ramadhan_akhir': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Kaaba_mirror_edit_jj.jpg/1200px-Kaaba_mirror_edit_jj.jpg',
        'path': 'packages/ramadhan-akhir-2025.jpg'
    },
    'december': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Masjid_Al_Nabawi.jpg/1200px-Masjid_Al_Nabawi.jpg',
        'path': 'packages/december-package-2026.jpg'
    },
    'baitul_maqdis_9': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Dome_of_the_rock_Jerusalem.jpg/1200px-Dome_of_the_rock_Jerusalem.jpg',
        'path': 'packages/baitul-maqdis-9days.jpg'
    },
    'baitul_maqdis_15': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Dome_of_the_rock_Jerusalem.jpg/1200px-Dome_of_the_rock_Jerusalem.jpg',
        'path': 'packages/baitul-maqdis-umrah-15days.jpg'
    },
    # Hotel images
    'rayhaan': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Makkah_-_panoramio_%284%29.jpg/1200px-Makkah_-_panoramio_%284%29.jpg',
        'path': 'hotels/rayhaan-rotana-makkah.jpg'
    },
    'azka': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Kaaba_mirror_edit_jj.jpg/1200px-Kaaba_mirror_edit_jj.jpg',
        'path': 'hotels/azka-almaqam-makkah.jpg'
    },
    'dallah': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Masjid_Al_Nabawi.jpg/1200px-Masjid_Al_Nabawi.jpg',
        'path': 'hotels/dallah-taibah-madinah.jpg'
    },
    'grand_court': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Dome_of_the_rock_Jerusalem.jpg/1200px-Dome_of_the_rock_Jerusalem.jpg',
        'path': 'hotels/grand-court-jerusalem.jpg'
    },
    'al_safwah': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Kaaba_mirror_edit_jj.jpg/1200px-Kaaba_mirror_edit_jj.jpg',
        'path': 'hotels/al-safwah-makkah.jpg'
    },
}

def prepare_images():
    """Download all images that don't already exist"""
    print("📥 Downloading images...")
    downloaded = {}
    for key, img in IMAGES.items():
        full_path = os.path.join(MEDIA_ROOT, img['path'])
        if os.path.exists(full_path):
            print(f"    ✅ Already exists: {img['path']}")
            downloaded[key] = img['path']
        else:
            result = download_image(img['url'], img['path'])
            downloaded[key] = result
    return downloaded


def add_packages():
    print("=" * 60)
    print("TM FOUZY - Add/Update Packages")
    print("=" * 60)

    # Get or guess categories
    umrah_cat = Category.objects.filter(category_type='umrah').first()
    ziarah_cat = Category.objects.filter(category_type='ziarah').first()

    if not umrah_cat:
        print("❌ Error: Umrah category not found. Please create it first.")
        return
    if not ziarah_cat:
        print("❌ Error: Ziarah category not found. Please create it first.")
        return

    # Download / verify images first
    imgs = prepare_images()

    packages_data = [
        # -------------------------------------------------------
        # 1. Ramadhan Awal
        # -------------------------------------------------------
        {
            'slug': 'umrah-ramadhan-awal-2025',
            'featured_image_key': 'ramadhan_awal',
            'hotel_image_key': 'rayhaan',
            'fields': {
                'name': 'Umrah Ramadhan - Awal Ramadhan Package',
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
            },
            'room_prices': [
                {'sharing_type': 'double', 'price': 4990},
                {'sharing_type': 'triple', 'price': 4790},
                {'sharing_type': 'quad',   'price': 4490},
            ]
        },
        # -------------------------------------------------------
        # 2. Ramadhan Akhir
        # -------------------------------------------------------
        {
            'slug': 'umrah-ramadhan-akhir-2025',
            'featured_image_key': 'ramadhan_akhir',
            'hotel_image_key': 'azka',
            'fields': {
                'name': 'Umrah Ramadhan - Akhir Ramadhan Package',
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
            },
            'room_prices': [
                {'sharing_type': 'double', 'price': 7890},
                {'sharing_type': 'triple', 'price': 6690},
                {'sharing_type': 'quad',   'price': 5690},
            ]
        },
        # -------------------------------------------------------
        # 3. December 1-11
        # -------------------------------------------------------
        {
            'slug': 'umrah-december-1-11-2026',
            'featured_image_key': 'december',
            'hotel_image_key': 'dallah',
            'fields': {
                'name': 'Umrah End Year Package - December 1-11',
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
                'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set, Zam Zam 2 liters',
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 4990},
                {'sharing_type': 'triple',         'price': 4690},
                {'sharing_type': 'quad',           'price': 4390},
                {'sharing_type': 'child_with_bed', 'price': 3990},
                {'sharing_type': 'child_no_bed',   'price': 2990},
            ]
        },
        # -------------------------------------------------------
        # 4. December 15-25
        # -------------------------------------------------------
        {
            'slug': 'umrah-december-15-25-2026',
            'featured_image_key': 'december',
            'hotel_image_key': 'dallah',
            'fields': {
                'name': 'Umrah End Year Package - December 15-25',
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
                'complimentary_items': 'Prayer mat, Zamzam bottle, Ihram set, Zam Zam 2 liters',
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 5390},
                {'sharing_type': 'triple',         'price': 5090},
                {'sharing_type': 'quad',           'price': 4790},
                {'sharing_type': 'child_with_bed', 'price': 4390},
                {'sharing_type': 'child_no_bed',   'price': 2990},
            ]
        },
        # -------------------------------------------------------
        # 5. Baitul Maqdis 9 Days
        # -------------------------------------------------------
        {
            'slug': 'baitul-maqdis-9-days-jan-2026',
            'featured_image_key': 'baitul_maqdis_9',
            'hotel_image_key': 'grand_court',
            'fields': {
                'name': 'The Sacred Journey - Baitul Maqdis (9 Days)',
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
                    {"day": 1, "title": "Amman Arrival",      "description": "Arrival at Amman, Jordan"},
                    {"day": 2, "title": "Petra Tour",          "description": "Full day tour of Petra ancient city"},
                    {"day": 3, "title": "Baitul Maqdis",       "description": "Visit Al-Aqsa Mosque and Dome of the Rock"},
                    {"day": 4, "title": "Jerusalem Old City",  "description": "Explore Jerusalem old city"},
                    {"day": 5, "title": "Hebron",              "description": "Visit Prophet Ibrahim tomb"},
                    {"day": 6, "title": "Bethlehem",           "description": "Visit Bethlehem and Church of Nativity"},
                    {"day": 7, "title": "Dead Sea",            "description": "Visit Dead Sea and surrounding area"},
                    {"day": 8, "title": "Amman City Tour",     "description": "Explore Amman city sights"},
                    {"day": 9, "title": "Departure",           "description": "Departure from Amman airport"},
                ],
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 4290},
                {'sharing_type': 'child_with_bed', 'price': 3690},
                {'sharing_type': 'child_no_bed',   'price': 3390},
            ]
        },
        # -------------------------------------------------------
        # 6. Baitul Maqdis + Umrah 15 Days
        # -------------------------------------------------------
        {
            'slug': 'umrah-baitul-maqdis-15-days-2025',
            'featured_image_key': 'baitul_maqdis_15',
            'hotel_image_key': 'al_safwah',
            'fields': {
                'name': 'The Sacred Journey - Umrah + Baitul Maqdis (15 Days)',
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
                    {"day": 1,  "title": "Amman Arrival",      "description": "Arrival at Amman, Jordan"},
                    {"day": 2,  "title": "Petra Tour",          "description": "Full day tour of Petra"},
                    {"day": 3,  "title": "Baitul Maqdis",       "description": "Visit Al-Aqsa Mosque"},
                    {"day": 4,  "title": "Jerusalem Old City",  "description": "Explore Jerusalem old city"},
                    {"day": 5,  "title": "Hebron & Bethlehem",  "description": "Visit Hebron and Bethlehem"},
                    {"day": 6,  "title": "Dead Sea",            "description": "Visit Dead Sea"},
                    {"day": 7,  "title": "Amman Departure",     "description": "Fly to Makkah via Madinah"},
                    {"day": 8,  "title": "Makkah Arrival",      "description": "Arrive in Makkah, perform Umrah"},
                    {"day": 9,  "title": "Makkah Ziarah",       "description": "Ziarah sites in Makkah"},
                    {"day": 10, "title": "Umrah",               "description": "Additional Umrah performance"},
                    {"day": 11, "title": "Makkah Free Day",     "description": "Free time for ibadah in Makkah"},
                    {"day": 12, "title": "Travel to Madinah",   "description": "High speed train to Madinah"},
                    {"day": 13, "title": "Masjid Nabawi",       "description": "Visit Masjid Nabawi and ziarah"},
                    {"day": 14, "title": "Madinah Ziarah",      "description": "Ziarah sites in Madinah"},
                    {"day": 15, "title": "Departure",           "description": "Departure from Madinah"},
                ],
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 6390},
                {'sharing_type': 'child_with_bed', 'price': 5090},
                {'sharing_type': 'child_no_bed',   'price': 4090},
            ]
        },
    ]

    created_count = 0
    updated_count = 0

    for pkg_data in packages_data:
        slug = pkg_data['slug']
        fields = pkg_data['fields']
        room_prices = pkg_data['room_prices']
        feat_img = imgs.get(pkg_data['featured_image_key'], '')
        hotel_img = imgs.get(pkg_data['hotel_image_key'], '')

        existing = Package.objects.filter(slug=slug).first()

        if existing:
            # UPDATE: override all fields + images
            for k, v in fields.items():
                setattr(existing, k, v)
            existing.slug = slug
            if feat_img:
                existing.featured_image = feat_img
            if hotel_img:
                existing.hotel_image = hotel_img
            existing.save()

            # Remove old room prices and re-add
            existing.room_prices.all().delete()
            for room in room_prices:
                RoomSharingPrice.objects.create(
                    package=existing,
                    sharing_type=room['sharing_type'],
                    price=room['price'],
                    available=True,
                    max_capacity=fields['max_capacity']
                )
            print(f"🔄 Updated: {fields['name']}")
            updated_count += 1

        else:
            # CREATE new package
            try:
                package = Package(**fields)
                package.slug = slug
                if feat_img:
                    package.featured_image = feat_img
                if hotel_img:
                    package.hotel_image = hotel_img
                package.save()

                for room in room_prices:
                    RoomSharingPrice.objects.create(
                        package=package,
                        sharing_type=room['sharing_type'],
                        price=room['price'],
                        available=True,
                        max_capacity=fields['max_capacity']
                    )
                print(f"✅ Created: {fields['name']}")
                created_count += 1
            except Exception as e:
                print(f"❌ Error creating {fields['name']}: {e}")

    print("=" * 60)
    print(f"✅ Created : {created_count} packages")
    print(f"🔄 Updated : {updated_count} packages")
    print("=" * 60)
    print("🎉 Done! Check: /admin/api/package/")
    print("=" * 60)


if __name__ == '__main__':
    add_packages()
