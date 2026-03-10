"""
QR Code Generation for ID Tags and Bag Tags
Generates QR codes with customer information for attendance tracking
"""

import qrcode
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import JsonResponse
from .models import Booking, Customer, Package
import json


def generate_qr_code_data(data_type, customer_data, package_data=None):
    """
    Generate QR code data based on type
    
    Args:
        data_type: 'id_tag' or 'bag_tag'
        customer_data: Customer information
        package_data: Package information
    
    Returns:
        dict: QR code data
    """
    base_url = getattr(settings, 'FRONTEND_URL', 'https://tmfouzy.sg')
    
    if data_type == 'id_tag':
        # ID Tag QR Code - Contains customer info for attendance tracking
        qr_data = {
            'type': 'id_tag',
            'customer_id': customer_data.get('id'),
            'name': customer_data.get('name'),
            'booking_number': customer_data.get('booking_number'),
            'package_id': package_data.get('id') if package_data else None,
            'package_name': package_data.get('name') if package_data else None,
            'emergency_contact': customer_data.get('emergency_contact'),
            'next_of_kin': customer_data.get('next_of_kin'),
            'hotel_contact': package_data.get('hotel_contact') if package_data else None,
            'scan_url': f"{base_url}/scan/id/{customer_data.get('id')}"
        }
    
    elif data_type == 'bag_tag':
        # Bag Tag QR Code - Contains room number for staff reference
        qr_data = {
            'type': 'bag_tag',
            'customer_id': customer_data.get('id'),
            'name': customer_data.get('name'),
            'booking_number': customer_data.get('booking_number'),
            'room_number': customer_data.get('room_number'),
            'hotel_name': customer_data.get('hotel_name'),
            'package_id': package_data.get('id') if package_data else None,
            'scan_url': f"{base_url}/scan/bag/{customer_data.get('id')}"
        }
    
    else:
        raise ValueError(f"Invalid data_type: {data_type}")
    
    return qr_data


def create_qr_code_image(data, size=(300, 300)):
    """
    Create QR code image from data
    
    Args:
        data: Data to encode in QR code
        size: QR code size (width, height)
    
    Returns:
        PIL Image: QR code image
    """
    # Convert data to JSON string
    qr_string = json.dumps(data)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize(size, Image.Resampling.LANCZOS)
    
    return qr_img


def create_id_tag(customer_data, package_data):
    """
    Create ID tag with QR code and customer information
    
    Args:
        customer_data: Customer information
        package_data: Package information
    
    Returns:
        str: Base64 encoded image
    """
    # Tag dimensions (in pixels)
    tag_width = 600
    tag_height = 400
    
    # Package color (default to green if not specified)
    package_color = package_data.get('color', '#2E7D32')
    
    # Create tag background
    tag_img = Image.new('RGB', (tag_width, tag_height), color='white')
    draw = ImageDraw.Draw(tag_img)
    
    # Draw colored header
    header_height = 80
    draw.rectangle([0, 0, tag_width, header_height], fill=package_color)
    
    # Generate QR code
    qr_data = generate_qr_code_data('id_tag', customer_data, package_data)
    qr_img = create_qr_code_image(qr_data, size=(150, 150))
    
    # Paste QR code on tag
    qr_x = tag_width - 170
    qr_y = 90
    tag_img.paste(qr_img, (qr_x, qr_y))
    
    # Add text information
    try:
        # Try to use a better font
        title_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header text
    draw.text((20, 25), "TM FOUZY TRAVEL & TOURS", fill='white', font=title_font)
    draw.text((20, 50), "ID TAG", fill='white', font=text_font)
    
    # Customer information
    y_pos = 100
    line_height = 25
    
    info_lines = [
        f"Name: {customer_data.get('name', 'N/A')}",
        f"Booking: {customer_data.get('booking_number', 'N/A')}",
        f"Package: {package_data.get('name', 'N/A')[:30]}...",
        f"Emergency: {customer_data.get('emergency_contact', 'N/A')}",
        f"Next of Kin: {customer_data.get('next_of_kin', 'N/A')}",
        f"Hotel: {package_data.get('hotel_contact', 'N/A')}"
    ]
    
    for line in info_lines:
        if y_pos < tag_height - 30:  # Don't overflow
            draw.text((20, y_pos), line, fill='black', font=text_font)
            y_pos += line_height
    
    # Footer
    draw.text((20, tag_height - 25), "Scan QR code for attendance", fill='gray', font=small_font)
    
    # Convert to base64
    buffer = io.BytesIO()
    tag_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str


def create_bag_tag(customer_data, package_data):
    """
    Create bag tag with QR code and room information
    
    Args:
        customer_data: Customer information
        package_data: Package information
    
    Returns:
        str: Base64 encoded image
    """
    # Tag dimensions (smaller for bag tag)
    tag_width = 400
    tag_height = 300
    
    # Package color
    package_color = package_data.get('color', '#2E7D32')
    
    # Create tag background
    tag_img = Image.new('RGB', (tag_width, tag_height), color='white')
    draw = ImageDraw.Draw(tag_img)
    
    # Draw colored header
    header_height = 60
    draw.rectangle([0, 0, tag_width, header_height], fill=package_color)
    
    # Generate QR code
    qr_data = generate_qr_code_data('bag_tag', customer_data, package_data)
    qr_img = create_qr_code_image(qr_data, size=(120, 120))
    
    # Paste QR code on tag
    qr_x = tag_width - 140
    qr_y = 70
    tag_img.paste(qr_img, (qr_x, qr_y))
    
    # Add text information
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        text_font = ImageFont.truetype("arial.ttf", 14)
        room_font = ImageFont.truetype("arial.ttf", 32)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        room_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header text
    draw.text((15, 15), "TM FOUZY", fill='white', font=title_font)
    draw.text((15, 35), "BAG TAG", fill='white', font=text_font)
    
    # Room number (large)
    room_number = customer_data.get('room_number', 'TBA')
    draw.text((20, 80), f"Room: {room_number}", fill=package_color, font=room_font)
    
    # Customer info
    y_pos = 130
    info_lines = [
        f"{customer_data.get('name', 'N/A')}",
        f"Booking: {customer_data.get('booking_number', 'N/A')}",
        f"Hotel: {customer_data.get('hotel_name', 'N/A')}"
    ]
    
    for line in info_lines:
        if y_pos < tag_height - 30:
            draw.text((20, y_pos), line, fill='black', font=text_font)
            y_pos += 20
    
    # Footer
    draw.text((20, tag_height - 25), "Scan for room info", fill='gray', font=small_font)
    
    # Convert to base64
    buffer = io.BytesIO()
    tag_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str


def generate_rooming_list_data(package_id):
    """
    Generate rooming list data for a package
    
    Args:
        package_id: Package ID
    
    Returns:
        dict: Rooming list data organized by rooms
    """
    try:
        package = Package.objects.get(id=package_id)
        bookings = Booking.objects.filter(package=package).select_related('customer')
        
        rooming_data = {
            'package': {
                'id': package.id,
                'name': package.name,
                'travel_date': package.travel_date,
                'location': package.location,
                'color': getattr(package, 'color', '#2E7D32')
            },
            'rooms': {},
            'total_customers': 0,
            'total_rooms': 0
        }
        
        for booking in bookings:
            # Get room assignments from booking rooms
            for room in booking.rooms.all():
                room_key = f"{room.hotel_name} - Room {room.room_number}"
                
                if room_key not in rooming_data['rooms']:
                    rooming_data['rooms'][room_key] = {
                        'hotel_name': room.hotel_name,
                        'room_number': room.room_number,
                        'room_type': room.sharing_type,
                        'customers': []
                    }
                
                # Add passengers to room
                for passenger in room.passengers.all():
                    customer_info = {
                        'id': passenger.id,
                        'name': passenger.full_name,
                        'booking_number': booking.booking_number,
                        'passenger_type': passenger.passenger_type,
                        'gender': passenger.gender,
                        'phone': passenger.phone or booking.contact_phone,
                        'emergency_contact': f"{booking.emergency_name} - {booking.emergency_phone}",
                        'next_of_kin': f"{booking.emergency_name} ({booking.emergency_relationship})"
                    }
                    rooming_data['rooms'][room_key]['customers'].append(customer_info)
                    rooming_data['total_customers'] += 1
        
        rooming_data['total_rooms'] = len(rooming_data['rooms'])
        
        return rooming_data
        
    except Package.DoesNotExist:
        raise ValueError(f"Package with ID {package_id} not found")
    except Exception as e:
        raise Exception(f"Error generating rooming list: {str(e)}")