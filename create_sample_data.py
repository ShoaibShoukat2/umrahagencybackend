"""
Run this script to create sample data for testing with HD images
Usage: python manage.py shell < create_sample_data.py
"""

from api.models import *
from django.utils.text import slugify
from datetime import datetime, timedelta

# Create Categories with HD Images
categories_data = [
    {
        'name': 'Umrah Packages', 
        'category_type': 'umrah', 
        'description': 'Sacred pilgrimage to Makkah and Madinah',
        'image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=1200&h=800&fit=crop'  # Kaaba HD
    },
    {
        'name': 'Hajj Packages', 
        'category_type': 'hajj', 
        'description': 'Complete Hajj pilgrimage packages',
        'image': 'https://images.unsplash.com/photo-1542816417-0983c9c9ad53?w=1200&h=800&fit=crop'  # Makkah HD
    },
    {
        'name': 'Ziarah Tours', 
        'category_type': 'ziarah', 
        'description': 'Visit historical Islamic sites',
        'image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=1200&h=800&fit=crop'  # Madinah HD
    },
    {
        'name': 'Holiday Packages', 
        'category_type': 'holiday', 
        'description': 'Relaxing holiday destinations',
        'image': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&h=800&fit=crop'  # Travel HD
    },
    {
        'name': 'Travel Items', 
        'category_type': 'item', 
        'description': 'Essential travel items',
        'image': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200&h=800&fit=crop'  # Travel items HD
    },
]

print("Creating categories...")
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        slug=slugify(cat_data['name']),
        defaults={
            'name': cat_data['name'],
            'category_type': cat_data['category_type'],
            'description': cat_data['description'],
            'image': cat_data.get('image', ''),
            'is_active': True,
            'order': 0
        }
    )
    if not created and cat_data.get('image'):
        cat.image = cat_data['image']
        cat.save()
    print(f"{'Created' if created else 'Updated'} category: {cat.name}")

# Create Tags
tags_data = ['Economy', 'Premium', 'Luxury', 'Family Friendly', 'Group Tour', 'Private Tour', 'Early Bird']

print("\nCreating tags...")
for tag_name in tags_data:
    tag, created = Tag.objects.get_or_create(
        slug=slugify(tag_name),
        defaults={'name': tag_name}
    )
    print(f"{'Created' if created else 'Found'} tag: {tag.name}")

# Create Sample Packages
umrah_cat = Category.objects.get(category_type='umrah')
hajj_cat = Category.objects.get(category_type='hajj')

# Create Sample Packages
umrah_cat = Category.objects.get(category_type='umrah')
hajj_cat = Category.objects.get(category_type='hajj')
ziarah_cat = Category.objects.get(category_type='ziarah')
holiday_cat = Category.objects.get(category_type='holiday')

packages_data = [
    # UMRAH PACKAGES
    {
        'category': umrah_cat,
        'name': '10 Days Umrah Package - Ramadan Special',
        'description': 'Experience the blessed month of Ramadan in the holy cities of Makkah and Madinah. This package includes accommodation near Haram, guided tours, and transportation. Perfect for families and groups seeking a spiritual journey during the most blessed month.',
        'short_description': 'Ramadan Umrah with premium hotels near Haram',
        'travel_date': datetime.now() + timedelta(days=60),
        'return_date': datetime.now() + timedelta(days=70),
        'duration_days': 10,
        'duration_nights': 9,
        'location': 'Makkah & Madinah',
        'itinerary': 'Day 1-5: Makkah (Haram visits, Umrah rituals, Ziyarat)\nDay 6-10: Madinah (Prophet\'s Mosque, historical sites)\nIncludes daily breakfast and dinner',
        'inclusions': '- Return flights\n- 4-star hotel accommodation\n- Daily breakfast & dinner\n- Airport transfers\n- Ziyarat tours\n- Visa processing\n- Experienced guide',
        'exclusions': '- Personal expenses\n- Lunch\n- Optional tours\n- Travel insurance',
        'min_deposit_amount': 500,
        'min_deposit_percentage': 20,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=1920&h=1080&fit=crop',
    },
    {
        'category': umrah_cat,
        'name': '7 Days Economy Umrah Package',
        'description': 'Affordable Umrah package perfect for families and groups. Comfortable accommodation with easy access to Haram. Budget-friendly without compromising on essential services.',
        'short_description': 'Budget-friendly Umrah package',
        'travel_date': datetime.now() + timedelta(days=45),
        'return_date': datetime.now() + timedelta(days=52),
        'duration_days': 7,
        'duration_nights': 6,
        'location': 'Makkah & Madinah',
        'itinerary': 'Day 1-4: Makkah (Umrah, Haram visits)\nDay 5-7: Madinah (Prophet\'s Mosque, Quba Mosque)',
        'inclusions': '- Return flights\n- 3-star hotel\n- Daily breakfast\n- Airport transfers\n- Visa processing',
        'exclusions': '- Meals (except breakfast)\n- Personal expenses\n- Optional tours',
        'min_deposit_amount': 300,
        'min_deposit_percentage': 20,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1542816417-0983c9c9ad53?w=1920&h=1080&fit=crop',
    },
    {
        'category': umrah_cat,
        'name': '14 Days Luxury Umrah Package',
        'description': 'Premium Umrah experience with 5-star hotels, VIP services, and exclusive tours. Enjoy the spiritual journey with maximum comfort and convenience.',
        'short_description': '5-star luxury Umrah with VIP services',
        'travel_date': datetime.now() + timedelta(days=90),
        'return_date': datetime.now() + timedelta(days=104),
        'duration_days': 14,
        'duration_nights': 13,
        'location': 'Makkah & Madinah',
        'itinerary': 'Day 1-7: Makkah (5-star hotel, Haram view)\nDay 8-14: Madinah (5-star hotel, Prophet\'s Mosque view)\nAll meals included',
        'inclusions': '- Business class flights\n- 5-star hotels with Haram view\n- All meals\n- VIP airport transfers\n- Private Ziyarat tours\n- Visa processing\n- Personal guide',
        'exclusions': '- Personal shopping\n- Optional activities',
        'min_deposit_amount': 1000,
        'min_deposit_percentage': 25,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=1920&h=1080&fit=crop',
    },
    
    # HAJJ PACKAGES
    {
        'category': hajj_cat,
        'name': '14 Days Hajj Package 2026',
        'description': 'Complete Hajj package with experienced guides, comfortable accommodation, and all necessary arrangements. Includes stay in Mina, Arafat, and Muzdalifah during Hajj days.',
        'short_description': 'Full Hajj package with premium services',
        'travel_date': datetime.now() + timedelta(days=120),
        'return_date': datetime.now() + timedelta(days=134),
        'duration_days': 14,
        'duration_nights': 13,
        'location': 'Makkah, Madinah, Mina, Arafat',
        'itinerary': 'Complete Hajj rituals with guided support\nDay 1-5: Makkah preparation\nDay 6-10: Hajj rituals (Mina, Arafat, Muzdalifah)\nDay 11-14: Madinah',
        'inclusions': '- Return flights\n- Accommodation in Makkah, Madinah, and Mina\n- All meals\n- Transportation\n- Experienced Hajj guides\n- Visa processing\n- Hajj kit',
        'exclusions': '- Personal expenses\n- Qurbani (optional)\n- Travel insurance',
        'min_deposit_amount': 1000,
        'min_deposit_percentage': 25,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1542816417-0983c9c9ad53?w=1920&h=1080&fit=crop',
    },
    {
        'category': hajj_cat,
        'name': '21 Days Premium Hajj Package',
        'description': 'Extended Hajj package with extra days for spiritual reflection and Ziyarat. Premium accommodation and comprehensive services throughout the journey.',
        'short_description': 'Extended Hajj with premium services',
        'travel_date': datetime.now() + timedelta(days=130),
        'return_date': datetime.now() + timedelta(days=151),
        'duration_days': 21,
        'duration_nights': 20,
        'location': 'Makkah, Madinah, Mina, Arafat',
        'itinerary': 'Day 1-8: Makkah (preparation & Umrah)\nDay 9-13: Hajj rituals\nDay 14-21: Madinah (extended stay)',
        'inclusions': '- Return flights\n- 4-star hotels\n- All meals\n- Transportation\n- Expert guides\n- Visa processing\n- Hajj kit\n- Extended Ziyarat tours',
        'exclusions': '- Personal expenses\n- Qurbani\n- Optional activities',
        'min_deposit_amount': 1500,
        'min_deposit_percentage': 30,
        'is_featured': False,
        'featured_image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=1920&h=1080&fit=crop',
    },
    
    # ZIARAH PACKAGES
    {
        'category': ziarah_cat,
        'name': '10 Days Islamic Heritage Tour',
        'description': 'Explore the rich Islamic heritage with visits to historical mosques, battlefields, and significant Islamic sites in Saudi Arabia.',
        'short_description': 'Historical Islamic sites tour',
        'travel_date': datetime.now() + timedelta(days=75),
        'return_date': datetime.now() + timedelta(days=85),
        'duration_days': 10,
        'duration_nights': 9,
        'location': 'Makkah, Madinah, Jeddah, Taif',
        'itinerary': 'Day 1-3: Makkah (Cave Hira, Cave Thawr)\nDay 4-6: Madinah (Quba, Qiblatain, Uhud)\nDay 7-8: Jeddah (historical sites)\nDay 9-10: Taif',
        'inclusions': '- Return flights\n- Hotel accommodation\n- Daily breakfast\n- Transportation\n- Expert guide\n- Visa processing\n- Entry fees',
        'exclusions': '- Lunch & dinner\n- Personal expenses\n- Optional activities',
        'min_deposit_amount': 400,
        'min_deposit_percentage': 20,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=1920&h=1080&fit=crop',
    },
    {
        'category': ziarah_cat,
        'name': '7 Days Madinah Ziyarat Special',
        'description': 'Focused tour of Madinah and surrounding historical Islamic sites. Perfect for those who want to spend more time in the city of the Prophet.',
        'short_description': 'Madinah-focused historical tour',
        'travel_date': datetime.now() + timedelta(days=65),
        'return_date': datetime.now() + timedelta(days=72),
        'duration_days': 7,
        'duration_nights': 6,
        'location': 'Madinah & Surroundings',
        'itinerary': 'Daily visits to Prophet\'s Mosque\nQuba Mosque, Qiblatain Mosque\nMount Uhud, Martyrs Cemetery\nDate farms, historical wells',
        'inclusions': '- Return flights\n- 3-star hotel near Haram\n- Daily breakfast\n- Transportation\n- Knowledgeable guide\n- Visa processing',
        'exclusions': '- Lunch & dinner\n- Personal expenses',
        'min_deposit_amount': 350,
        'min_deposit_percentage': 20,
        'is_featured': False,
        'featured_image': 'https://images.unsplash.com/photo-1542816417-0983c9c9ad53?w=1920&h=1080&fit=crop',
    },
    
    # HOLIDAY PACKAGES
    {
        'category': holiday_cat,
        'name': '7 Days Dubai Shopping & Sightseeing',
        'description': 'Experience the glamour of Dubai with shopping, sightseeing, and entertainment. Visit iconic landmarks, luxury malls, and enjoy desert safari.',
        'short_description': 'Dubai holiday with shopping and tours',
        'travel_date': datetime.now() + timedelta(days=50),
        'return_date': datetime.now() + timedelta(days=57),
        'duration_days': 7,
        'duration_nights': 6,
        'location': 'Dubai, UAE',
        'itinerary': 'Day 1: Arrival, Dubai Mall\nDay 2: Burj Khalifa, Dubai Fountain\nDay 3: Desert Safari\nDay 4: Dubai Marina, JBR Beach\nDay 5: Gold Souk, Spice Souk\nDay 6: Shopping day\nDay 7: Departure',
        'inclusions': '- Return flights\n- 4-star hotel\n- Daily breakfast\n- Airport transfers\n- Desert safari\n- City tour\n- Visa processing',
        'exclusions': '- Lunch & dinner\n- Shopping expenses\n- Optional activities\n- Travel insurance',
        'min_deposit_amount': 400,
        'min_deposit_percentage': 20,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1920&h=1080&fit=crop',
    },
    {
        'category': holiday_cat,
        'name': '10 Days Turkey Cultural Tour',
        'description': 'Discover the beauty of Turkey with visits to Istanbul, Cappadocia, and Pamukkale. Experience rich history, stunning landscapes, and delicious cuisine.',
        'short_description': 'Turkey cultural and historical tour',
        'travel_date': datetime.now() + timedelta(days=80),
        'return_date': datetime.now() + timedelta(days=90),
        'duration_days': 10,
        'duration_nights': 9,
        'location': 'Istanbul, Cappadocia, Pamukkale',
        'itinerary': 'Day 1-4: Istanbul (Blue Mosque, Hagia Sophia, Grand Bazaar)\nDay 5-7: Cappadocia (Hot air balloon, underground cities)\nDay 8-9: Pamukkale (Thermal pools)\nDay 10: Return',
        'inclusions': '- Return flights\n- 4-star hotels\n- Daily breakfast\n- Internal flights\n- Transportation\n- Guided tours\n- Visa processing',
        'exclusions': '- Lunch & dinner\n- Hot air balloon ride\n- Personal expenses\n- Travel insurance',
        'min_deposit_amount': 500,
        'min_deposit_percentage': 25,
        'is_featured': True,
        'featured_image': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1920&h=1080&fit=crop',
    },
    {
        'category': holiday_cat,
        'name': '5 Days Bali Beach Retreat',
        'description': 'Relax and unwind in the tropical paradise of Bali. Enjoy beautiful beaches, temples, rice terraces, and Balinese culture.',
        'short_description': 'Bali beach and cultural retreat',
        'travel_date': datetime.now() + timedelta(days=40),
        'return_date': datetime.now() + timedelta(days=45),
        'duration_days': 5,
        'duration_nights': 4,
        'location': 'Bali, Indonesia',
        'itinerary': 'Day 1: Arrival, beach relaxation\nDay 2: Ubud (rice terraces, monkey forest)\nDay 3: Temple tours (Tanah Lot, Uluwatu)\nDay 4: Water sports, beach activities\nDay 5: Departure',
        'inclusions': '- Return flights\n- Beach resort accommodation\n- Daily breakfast\n- Airport transfers\n- Temple tours\n- Visa on arrival',
        'exclusions': '- Lunch & dinner\n- Water sports\n- Personal expenses\n- Travel insurance',
        'min_deposit_amount': 300,
        'min_deposit_percentage': 20,
        'is_featured': False,
        'featured_image': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1920&h=1080&fit=crop',
    },
]

print("\nCreating packages...")
for pkg_data in packages_data:
    pkg, created = Package.objects.get_or_create(
        slug=slugify(pkg_data['name']),
        defaults=pkg_data
    )
    if not created and pkg_data.get('featured_image'):
        pkg.featured_image = pkg_data['featured_image']
        pkg.save()
    print(f"{'Created' if created else 'Updated'} package: {pkg.name}")
    
    # Add package gallery images
    if created:
        gallery_images = [
            {'caption': 'Kaaba View', 'image': 'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=1920&h=1080&fit=crop', 'order': 1},
            {'caption': 'Hotel Exterior', 'image': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1920&h=1080&fit=crop', 'order': 2},
            {'caption': 'Room Interior', 'image': 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=1920&h=1080&fit=crop', 'order': 3},
            {'caption': 'Madinah Mosque', 'image': 'https://images.unsplash.com/photo-1564769625905-50e93615e769?w=1920&h=1080&fit=crop', 'order': 4},
        ]
        
        for img_data in gallery_images:
            PackageImage.objects.create(
                package=pkg,
                image=img_data['image'],
                caption=img_data['caption'],
                order=img_data['order']
            )
        print(f"  Added gallery images for {pkg.name}")
    
    # Add room prices
    if created:
        room_prices = [
            {'sharing_type': 'single', 'price': 3500},
            {'sharing_type': 'double', 'price': 2500},
            {'sharing_type': 'triple', 'price': 2000},
            {'sharing_type': 'quad', 'price': 1800},
        ]
        
        for rp_data in room_prices:
            RoomSharingPrice.objects.create(
                package=pkg,
                sharing_type=rp_data['sharing_type'],
                price=rp_data['price'],
                available=True,
                max_capacity=50
            )
        print(f"  Added room prices for {pkg.name}")
        
        # Add some add-ons
        addons = [
            {'name': 'Extra Luggage (20kg)', 'addon_type': 'person', 'price': 50, 'description': 'Additional 20kg luggage allowance'},
            {'name': 'Business Class Upgrade', 'addon_type': 'flight', 'price': 800, 'description': 'Upgrade to business class'},
            {'name': 'Private Room Service', 'addon_type': 'room', 'price': 200, 'description': 'Daily room service'},
            {'name': 'Airport Lounge Access', 'addon_type': 'other', 'price': 75, 'description': 'Access to VIP lounge'},
        ]
        
        for addon_data in addons:
            AddOn.objects.create(
                package=pkg,
                name=addon_data['name'],
                addon_type=addon_data['addon_type'],
                price=addon_data['price'],
                description=addon_data['description'],
                is_active=True
            )
        print(f"  Added add-ons for {pkg.name}")
        
        # Add tags
        economy_tag = Tag.objects.get(slug='economy')
        premium_tag = Tag.objects.get(slug='premium')
        family_tag = Tag.objects.get(slug='family-friendly')
        
        if 'Economy' in pkg.name:
            pkg.tags.add(economy_tag, family_tag)
        else:
            pkg.tags.add(premium_tag, family_tag)

# Create Travel Items
items_cat = Category.objects.get(category_type='item')

items_data = [
    {
        'name': 'Ihram Set (2 pieces)', 
        'price': 25, 
        'description': 'High-quality cotton Ihram set for Umrah and Hajj', 
        'stock_quantity': 100,
        'image': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&h=800&fit=crop'  # White fabric
    },
    {
        'name': 'Prayer Mat', 
        'price': 15, 
        'description': 'Portable prayer mat with carrying case and compass', 
        'stock_quantity': 150,
        'image': 'https://images.unsplash.com/photo-1609599006353-e629aaabfeae?w=800&h=800&fit=crop'  # Prayer mat
    },
    {
        'name': 'Travel Dua Book', 
        'price': 10, 
        'description': 'Essential duas for travelers in Arabic and English', 
        'stock_quantity': 200,
        'image': 'https://images.unsplash.com/photo-1585842378054-ee2e52f94ba2?w=800&h=800&fit=crop'  # Islamic book
    },
    {
        'name': 'Zamzam Water Bottle', 
        'price': 5, 
        'description': 'BPA-free water bottle for Zamzam water', 
        'stock_quantity': 300,
        'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&h=800&fit=crop'  # Water bottle
    },
    {
        'name': 'Travel Backpack', 
        'price': 45, 
        'description': 'Durable travel backpack with multiple compartments', 
        'stock_quantity': 80,
        'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=800&fit=crop'  # Backpack
    },
    {
        'name': 'Tasbeeh Counter', 
        'price': 8, 
        'description': 'Digital tasbeeh counter with LED display', 
        'stock_quantity': 120,
        'image': 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&h=800&fit=crop'  # Prayer beads
    },
]

print("\nCreating travel items...")
for item_data in items_data:
    item, created = TravelItem.objects.get_or_create(
        slug=slugify(item_data['name']),
        defaults={
            'category': items_cat,
            'name': item_data['name'],
            'price': item_data['price'],
            'description': item_data['description'],
            'stock_quantity': item_data['stock_quantity'],
            'image': item_data.get('image', ''),
            'is_active': True
        }
    )
    if not created and item_data.get('image'):
        item.image = item_data['image']
        item.save()
    print(f"{'Created' if created else 'Updated'} item: {item.name}")

print("\n✅ Sample data with HD images created successfully!")
print("\n📸 HD Images Added:")
print("  - Categories: Professional HD images")
print("  - Packages: Featured images + Gallery (4 images each)")
print("  - Travel Items: Product images")
print("\nYou can now:")
print("1. Access admin panel at http://localhost:8000/admin")
print("2. View packages at http://localhost:3000")
print("3. Create bookings and test the customer portal")
print("4. All images are HD quality from Unsplash")
print("\n🎨 Site looks professional now!")
