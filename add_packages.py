#!/usr/bin/env python
"""
TM FOUZY - PACKAGES + TRAVEL ITEMS UPDATE SCRIPT
- Downloads relevant Islamic images from Pexels (verified working URLs)
- Creates packages if not exist, UPDATES if already exist (images override)
- Creates travel items if not exist, UPDATES if already exist (images override)

Run: python add_packages.py
"""
import os
import sys
import django
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Package, RoomSharingPrice, Category, TravelItem
from backend.settings import MEDIA_ROOT

# ================================================================
# VERIFIED WORKING IMAGE URLS (Pexels - free, no auth needed)
# All are Islamic / travel relevant photos
# ================================================================
IMAGES = {

    # ---- PACKAGE FEATURED IMAGES ----

    # Kaaba / Masjidil Haram - Makkah (for Ramadhan packages)
    'pkg_ramadhan_awal': {
        'url': 'https://images.pexels.com/photos/32290180/pexels-photo-32290180.jpeg?w=800&h=600&fit=crop',
        'path': 'packages/ramadhan-awal-2025.jpg',
    },
    # Masjidil Haram aerial - Makkah (for Ramadhan Akhir)
    'pkg_ramadhan_akhir': {
        'url': 'https://images.pexels.com/photos/34981831/pexels-photo-34981831.jpeg?w=800&h=600&fit=crop',
        'path': 'packages/ramadhan-akhir-2025.jpg',
    },
    # Masjid Nabawi - Madinah (for December packages)
    'pkg_december': {
        'url': 'https://images.pexels.com/photos/3617500/pexels-photo-3617500.jpeg?w=800&h=600&fit=crop',
        'path': 'packages/december-package-2026.jpg',
    },
    # Dome of the Rock / Al-Aqsa - Jerusalem (Baitul Maqdis 9 days)
    'pkg_baitul_maqdis_9': {
        'url': 'https://images.pexels.com/photos/3601425/pexels-photo-3601425.jpeg?w=800&h=600&fit=crop',
        'path': 'packages/baitul-maqdis-9days.jpg',
    },
    # Al-Aqsa Mosque Jerusalem (Baitul Maqdis 15 days)
    'pkg_baitul_maqdis_15': {
        'url': 'https://images.pexels.com/photos/4861376/pexels-photo-4861376.jpeg?w=800&h=600&fit=crop',
        'path': 'packages/baitul-maqdis-umrah-15days.jpg',
    },

    # ---- HOTEL IMAGES ----

    # Makkah hotel (Rayhaan by Rotana / Azka)
    'hotel_makkah': {
        'url': 'https://images.pexels.com/photos/2087391/pexels-photo-2087391.jpeg?w=800&h=600&fit=crop',
        'path': 'hotels/rayhaan-rotana-makkah.jpg',
    },
    # Azka Al-Maqam Makkah hotel
    'hotel_azka': {
        'url': 'https://images.pexels.com/photos/5273046/pexels-photo-5273046.jpeg?w=800&h=600&fit=crop',
        'path': 'hotels/azka-almaqam-makkah.jpg',
    },
    # Dallah Taibah - Madinah hotel
    'hotel_madinah': {
        'url': 'https://images.pexels.com/photos/3709400/pexels-photo-3709400.jpeg?w=800&h=600&fit=crop',
        'path': 'hotels/dallah-taibah-madinah.jpg',
    },
    # Grand Court - Jerusalem hotel
    'hotel_jerusalem': {
        'url': 'https://images.pexels.com/photos/3566187/pexels-photo-3566187.jpeg?w=800&h=600&fit=crop',
        'path': 'hotels/grand-court-jerusalem.jpg',
    },
    # Al Safwah - Makkah hotel
    'hotel_safwah': {
        'url': 'https://images.pexels.com/photos/7249378/pexels-photo-7249378.jpeg?w=800&h=600&fit=crop',
        'path': 'hotels/al-safwah-makkah.jpg',
    },

    # ---- TRAVEL ITEMS IMAGES ----

    # Ihram set - white cloth/fabric
    'item_ihram': {
        'url': 'https://images.pexels.com/photos/6044266/pexels-photo-6044266.jpeg?w=400&h=400&fit=crop',
        'path': 'items/ihram-set-men.jpg',
    },
    # Prayer mat - sajadah
    'item_prayer_mat': {
        'url': 'https://images.pexels.com/photos/6044198/pexels-photo-6044198.jpeg?w=400&h=400&fit=crop',
        'path': 'items/prayer-mat.jpg',
    },
    # Water bottle - Zamzam
    'item_zamzam': {
        'url': 'https://images.pexels.com/photos/1000084/pexels-photo-1000084.jpeg?w=400&h=400&fit=crop',
        'path': 'items/zamzam-bottle-5l.jpg',
    },
    # Tasbih / prayer beads
    'item_tasbih': {
        'url': 'https://images.pexels.com/photos/6044262/pexels-photo-6044262.jpeg?w=400&h=400&fit=crop',
        'path': 'items/travel-tasbih.jpg',
    },
    # Book / Quran guide
    'item_book': {
        'url': 'https://images.pexels.com/photos/6044228/pexels-photo-6044228.jpeg?w=400&h=400&fit=crop',
        'path': 'items/umrah-guide-book.jpg',
    },
}


def download_image(url, filepath):
    """Download image, force re-download (override existing)"""
    try:
        folder = os.path.dirname(filepath)
        full_folder = os.path.join(MEDIA_ROOT, folder)
        os.makedirs(full_folder, exist_ok=True)
        full_path = os.path.join(MEDIA_ROOT, filepath)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.pexels.com/',
        }
        req = urllib.request.Request(url, headers=headers)
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        with opener.open(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 2000:
                raise Exception(f"File too small ({len(data)} bytes) - likely error page")
            with open(full_path, 'wb') as f:
                f.write(data)
        print(f"    📸 Downloaded ({len(data)//1024}KB): {filepath}")
        return filepath
    except Exception as e:
        print(f"    ⚠️  Failed: {filepath} — {e}")
        return ''


def prepare_all_images(force=False):
    """Download all images. force=True re-downloads even if exists."""
    print("\n📥 Downloading images (force override)...")
    result = {}
    for key, img in IMAGES.items():
        full_path = os.path.join(MEDIA_ROOT, img['path'])
        if not force and os.path.exists(full_path) and os.path.getsize(full_path) > 2000:
            print(f"    ✅ Exists: {img['path']}")
            result[key] = img['path']
        else:
            # Delete old file first
            if os.path.exists(full_path):
                os.remove(full_path)
            r = download_image(img['url'], img['path'])
            result[key] = r
    return result


# ================================================================
# PACKAGES DATA
# ================================================================
def get_packages_data(umrah_cat, ziarah_cat, imgs):
    return [
        # 1. Ramadhan Awal
        {
            'slug': 'umrah-ramadhan-awal-2025',
            'feat_img': imgs.get('pkg_ramadhan_awal', ''),
            'hotel_img': imgs.get('hotel_makkah', ''),
            'fields': {
                'name': 'Umrah Ramadhan - Awal Ramadhan Package',
                'category': umrah_cat,
                'short_description': 'Ibadah yang lebih bermakna di bulan yang mulia - Awal Ramadhan 4-15 Feb 2025',
                'description': 'Paket Umrah Ramadhan di awal bulan suci dengan hotel premium Rayhaan by Rotana (Makkah) dan Dallah Taibah Hotel (Madinah). Full board meal, guided umrah 3x.',
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
            ],
        },
        # 2. Ramadhan Akhir
        {
            'slug': 'umrah-ramadhan-akhir-2025',
            'feat_img': imgs.get('pkg_ramadhan_akhir', ''),
            'hotel_img': imgs.get('hotel_azka', ''),
            'fields': {
                'name': 'Umrah Ramadhan - Akhir Ramadhan Package',
                'category': umrah_cat,
                'short_description': 'Ibadah yang lebih bermakna di bulan yang mulia - Akhir Ramadhan 27 Feb - 12 Mar 2025',
                'description': 'Paket Umrah Ramadhan di akhir bulan suci dengan hotel premium Azka Al-Maqam (Makkah) dan Dallah Taibah Hotel (Madinah). Termasuk full board meal dan guided umrah.',
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
            ],
        },
        # 3. December 1-11
        {
            'slug': 'umrah-december-1-11-2026',
            'feat_img': imgs.get('pkg_december', ''),
            'hotel_img': imgs.get('hotel_madinah', ''),
            'fields': {
                'name': 'Umrah End Year Package - December 1-11',
                'category': umrah_cat,
                'short_description': 'End of Year Umrah Package Dec 2026 - Rayhaan by Rotana Makkah, Dallah Taibah Madinah',
                'description': 'End year Umrah package with 5-star hotels: Rayhaan by Rotana (Makkah) and Dallah Taibah Hotel (Madinah). Includes full board meal, high speed train, and guided tours.',
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
            ],
        },
        # 4. December 15-25
        {
            'slug': 'umrah-december-15-25-2026',
            'feat_img': imgs.get('pkg_december', ''),
            'hotel_img': imgs.get('hotel_madinah', ''),
            'fields': {
                'name': 'Umrah End Year Package - December 15-25',
                'category': umrah_cat,
                'short_description': 'End of Year Umrah Package Dec 2026 - Premium 5-Star Hotels',
                'description': 'End year Umrah package with 5-star hotels: Rayhaan by Rotana (Makkah) and Dallah Taibah Hotel (Madinah). Includes full board meal, high speed train, and guided tours.',
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
            ],
        },
        # 5. Baitul Maqdis 9 Days
        {
            'slug': 'baitul-maqdis-9-days-jan-2026',
            'feat_img': imgs.get('pkg_baitul_maqdis_9', ''),
            'hotel_img': imgs.get('hotel_jerusalem', ''),
            'fields': {
                'name': 'The Sacred Journey - Baitul Maqdis (9 Days)',
                'category': ziarah_cat,
                'short_description': 'Amman, Petra, Baitul Maqdis - 9 Days Sacred Journey with Ustaz TM Fauwaz',
                'description': 'Jelajah Bumi Anbiya - Visit Petra, Baitul Maqdis (Al-Aqsa & Dome of Rock), Hebron, and Dead Sea. Guided by Ustaz TM Fauwaz.',
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
                    {"day": 1, "title": "Amman Arrival",     "description": "Arrival at Amman, Jordan. Transfer to hotel."},
                    {"day": 2, "title": "Petra Tour",         "description": "Full day tour of Petra - The Rose City ancient wonder."},
                    {"day": 3, "title": "Baitul Maqdis",      "description": "Visit Al-Aqsa Mosque and Dome of the Rock - Jerusalem."},
                    {"day": 4, "title": "Jerusalem Old City", "description": "Explore Jerusalem old city walls and historic sites."},
                    {"day": 5, "title": "Hebron",             "description": "Visit Cave of Machpelah - Tomb of Prophet Ibrahim AS."},
                    {"day": 6, "title": "Bethlehem",          "description": "Visit Bethlehem and surrounding holy sites."},
                    {"day": 7, "title": "Dead Sea",           "description": "Float in the Dead Sea - lowest point on earth."},
                    {"day": 8, "title": "Amman City Tour",    "description": "Explore Amman city - Roman Amphitheatre and markets."},
                    {"day": 9, "title": "Departure",          "description": "Check out and transfer to Amman airport. Farewell!"},
                ],
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 4290},
                {'sharing_type': 'child_with_bed', 'price': 3690},
                {'sharing_type': 'child_no_bed',   'price': 3390},
            ],
        },
        # 6. Baitul Maqdis + Umrah 15 Days
        {
            'slug': 'umrah-baitul-maqdis-15-days-2025',
            'feat_img': imgs.get('pkg_baitul_maqdis_15', ''),
            'hotel_img': imgs.get('hotel_safwah', ''),
            'fields': {
                'name': 'The Sacred Journey - Umrah + Baitul Maqdis (15 Days)',
                'category': ziarah_cat,
                'short_description': 'Amman, Petra, Baitul Maqdis + Umrah - 15 Days Complete Journey',
                'description': 'Complete package: Baitul Maqdis (Jerusalem, Petra, Hebron) + Umrah (Makkah, Madinah). Guided by Ustaz TM Fauwaz. Best of both sacred destinations.',
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
                    {"day": 1,  "title": "Amman Arrival",     "description": "Arrival at Amman, Jordan. Check-in hotel."},
                    {"day": 2,  "title": "Petra Tour",         "description": "Full day tour of Petra ancient city."},
                    {"day": 3,  "title": "Baitul Maqdis",      "description": "Visit Al-Aqsa Mosque and Dome of the Rock."},
                    {"day": 4,  "title": "Jerusalem Old City", "description": "Explore Jerusalem old city."},
                    {"day": 5,  "title": "Hebron & Bethlehem", "description": "Visit Hebron (Tomb of Ibrahim AS) and Bethlehem."},
                    {"day": 6,  "title": "Dead Sea",           "description": "Visit Dead Sea."},
                    {"day": 7,  "title": "Travel to Makkah",   "description": "Fly from Amman to Jeddah, transfer to Makkah."},
                    {"day": 8,  "title": "Umrah",              "description": "Arrive Makkah. Perform Umrah. Check-in hotel."},
                    {"day": 9,  "title": "Makkah Ziarah",      "description": "Ziarah sites in Makkah - Arafah, Mina, Muzdalifah."},
                    {"day": 10, "title": "Ibadah Makkah",      "description": "Free time for ibadah and tawaf in Masjidil Haram."},
                    {"day": 11, "title": "Makkah Free Day",    "description": "Free time for shopping and personal ibadah."},
                    {"day": 12, "title": "Travel to Madinah",  "description": "High speed train from Makkah to Madinah."},
                    {"day": 13, "title": "Masjid Nabawi",      "description": "Visit Masjid Nabawi, Raudhah, and Quba Mosque."},
                    {"day": 14, "title": "Madinah Ziarah",     "description": "Ziarah sites in Madinah - Uhud, Qiblatayn Mosque."},
                    {"day": 15, "title": "Departure",          "description": "Transfer to Madinah airport. Farewell!"},
                ],
            },
            'room_prices': [
                {'sharing_type': 'double',         'price': 6390},
                {'sharing_type': 'child_with_bed', 'price': 5090},
                {'sharing_type': 'child_no_bed',   'price': 4090},
            ],
        },
    ]


# ================================================================
# TRAVEL ITEMS DATA
# ================================================================
def get_items_data(item_cat, imgs):
    return [
        {
            'slug': 'ihram-set-men',
            'image_key': 'item_ihram',
            'fields': {
                'name': 'Ihram Set (Men)',
                'category': item_cat,
                'description': 'Complete Ihram set for men. Includes 2 pieces of high quality white cotton towels. Lightweight and comfortable for Umrah and Hajj.',
                'price': 25.00,
                'stock_quantity': 100,
                'is_active': True,
            },
        },
        {
            'slug': 'prayer-mat',
            'image_key': 'item_prayer_mat',
            'fields': {
                'name': 'Travel Prayer Mat (Sejadah)',
                'category': item_cat,
                'description': 'Portable travel prayer mat (Sejadah). Lightweight, foldable, and easy to carry. Perfect for travel and outdoor prayers.',
                'price': 15.00,
                'stock_quantity': 150,
                'is_active': True,
            },
        },
        {
            'slug': 'zamzam-bottle-5l',
            'image_key': 'item_zamzam',
            'fields': {
                'name': 'Zamzam Water Bottle (5L)',
                'category': item_cat,
                'description': 'Premium Zamzam water 5 liters. Sealed and certified. Direct from Makkah. Blessed water for health and barakah.',
                'price': 20.00,
                'stock_quantity': 200,
                'is_active': True,
            },
        },
        {
            'slug': 'travel-tasbih',
            'image_key': 'item_tasbih',
            'fields': {
                'name': 'Digital Tasbih Counter',
                'category': item_cat,
                'description': 'Digital tasbih counter with wrist strap. Easy one-click counting. Perfect for dhikr during Umrah, Hajj, and daily prayers.',
                'price': 12.00,
                'stock_quantity': 80,
                'is_active': True,
            },
        },
        {
            'slug': 'umrah-guide-book',
            'image_key': 'item_book',
            'fields': {
                'name': 'Umrah Guide Book',
                'category': item_cat,
                'description': 'Comprehensive Umrah guide book with step-by-step instructions, duas in Arabic with transliteration and translation. Essential for every pilgrim.',
                'price': 18.00,
                'stock_quantity': 60,
                'is_active': True,
            },
        },
    ]


# ================================================================
# MAIN
# ================================================================
def run():
    print("=" * 60)
    print("TM FOUZY - Packages + Travel Items Update")
    print("=" * 60)

    umrah_cat  = Category.objects.filter(category_type='umrah').first()
    ziarah_cat = Category.objects.filter(category_type='ziarah').first()
    item_cat   = Category.objects.filter(category_type='item').first()

    if not umrah_cat:
        print("❌ Umrah category not found!")
        return
    if not ziarah_cat:
        print("❌ Ziarah category not found!")
        return
    if not item_cat:
        print("⚠️  Item category not found - travel items will be skipped")

    # Force re-download all images (removes old irrelevant ones)
    imgs = prepare_all_images(force=True)

    # ---- UPDATE PACKAGES ----
    print("\n📦 Updating Packages...")
    packages = get_packages_data(umrah_cat, ziarah_cat, imgs)
    created_pkg = updated_pkg = 0

    for pkg in packages:
        slug      = pkg['slug']
        fields    = pkg['fields']
        feat_img  = pkg['feat_img']
        hotel_img = pkg['hotel_img']
        prices    = pkg['room_prices']

        existing = Package.objects.filter(slug=slug).first()
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            if feat_img:
                existing.featured_image = feat_img
            if hotel_img:
                existing.hotel_image = hotel_img
            existing.save()
            existing.room_prices.all().delete()
            for r in prices:
                RoomSharingPrice.objects.create(
                    package=existing,
                    sharing_type=r['sharing_type'],
                    price=r['price'],
                    available=True,
                    max_capacity=fields['max_capacity'],
                )
            print(f"  🔄 Updated: {fields['name']}")
            updated_pkg += 1
        else:
            obj = Package(slug=slug, **fields)
            if feat_img:
                obj.featured_image = feat_img
            if hotel_img:
                obj.hotel_image = hotel_img
            obj.save()
            for r in prices:
                RoomSharingPrice.objects.create(
                    package=obj,
                    sharing_type=r['sharing_type'],
                    price=r['price'],
                    available=True,
                    max_capacity=fields['max_capacity'],
                )
            print(f"  ✅ Created: {fields['name']}")
            created_pkg += 1

    # ---- UPDATE TRAVEL ITEMS ----
    print("\n🛍️  Updating Travel Items...")
    created_item = updated_item = 0

    if item_cat:
        items = get_items_data(item_cat, imgs)
        for item in items:
            slug      = item['slug']
            fields    = item['fields']
            item_img  = imgs.get(item['image_key'], '')

            existing = TravelItem.objects.filter(slug=slug).first()
            if existing:
                for k, v in fields.items():
                    setattr(existing, k, v)
                if item_img:
                    existing.image = item_img
                existing.save()
                print(f"  🔄 Updated: {fields['name']}")
                updated_item += 1
            else:
                obj = TravelItem(slug=slug, **fields)
                if item_img:
                    obj.image = item_img
                obj.save()
                print(f"  ✅ Created: {fields['name']}")
                created_item += 1
    else:
        print("  ⚠️  Skipped (no item category)")

    # ---- SUMMARY ----
    print("\n" + "=" * 60)
    print(f"  📦 Packages  — Created: {created_pkg}  Updated: {updated_pkg}")
    print(f"  🛍️  Items     — Created: {created_item}  Updated: {updated_item}")
    print("=" * 60)
    print("🎉 Done! Check admin: /admin/api/package/")
    print("=" * 60)


if __name__ == '__main__':
    run()
