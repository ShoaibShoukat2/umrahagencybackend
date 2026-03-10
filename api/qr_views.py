"""
QR Code and Rooming List Views
Handles generation of ID tags, bag tags, and rooming lists
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Package, Booking, Customer
from .qr_code_generator import (
    create_id_tag, 
    create_bag_tag, 
    generate_rooming_list_data,
    generate_qr_code_data
)
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_id_tag(request, customer_id):
    """
    Generate ID tag with QR code for a customer
    
    URL: /api/qr/id-tag/{customer_id}/
    """
    try:
        # Get customer and booking info
        customer = get_object_or_404(Customer, id=customer_id)
        booking = Booking.objects.filter(customer=customer).first()
        
        if not booking:
            return Response(
                {'error': 'No booking found for this customer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare customer data
        customer_data = {
            'id': customer.id,
            'name': customer.user.first_name if customer.user else customer.email,
            'booking_number': booking.booking_number,
            'emergency_contact': f"{booking.emergency_name} - {booking.emergency_phone}",
            'next_of_kin': f"{booking.emergency_name} ({booking.emergency_relationship})"
        }
        
        # Prepare package data
        package_data = {
            'id': booking.package.id,
            'name': booking.package.name,
            'color': getattr(booking.package, 'color', '#2E7D32'),
            'hotel_contact': getattr(booking.package, 'hotel_contact', 'Contact tour leader')
        }
        
        # Generate ID tag
        id_tag_base64 = create_id_tag(customer_data, package_data)
        
        return Response({
            'success': True,
            'customer_name': customer_data['name'],
            'booking_number': customer_data['booking_number'],
            'package_name': package_data['name'],
            'id_tag_image': f"data:image/png;base64,{id_tag_base64}",
            'qr_data': generate_qr_code_data('id_tag', customer_data, package_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_bag_tag(request, customer_id):
    """
    Generate bag tag with QR code for a customer
    
    URL: /api/qr/bag-tag/{customer_id}/
    """
    try:
        # Get customer and booking info
        customer = get_object_or_404(Customer, id=customer_id)
        booking = Booking.objects.filter(customer=customer).first()
        
        if not booking:
            return Response(
                {'error': 'No booking found for this customer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get room assignment
        room = booking.rooms.first()
        room_number = room.room_number if room else 'TBA'
        hotel_name = room.hotel_name if room else 'TBA'
        
        # Prepare customer data
        customer_data = {
            'id': customer.id,
            'name': customer.user.first_name if customer.user else customer.email,
            'booking_number': booking.booking_number,
            'room_number': room_number,
            'hotel_name': hotel_name
        }
        
        # Prepare package data
        package_data = {
            'id': booking.package.id,
            'name': booking.package.name,
            'color': getattr(booking.package, 'color', '#2E7D32')
        }
        
        # Generate bag tag
        bag_tag_base64 = create_bag_tag(customer_data, package_data)
        
        return Response({
            'success': True,
            'customer_name': customer_data['name'],
            'booking_number': customer_data['booking_number'],
            'room_number': room_number,
            'hotel_name': hotel_name,
            'bag_tag_image': f"data:image/png;base64,{bag_tag_base64}",
            'qr_data': generate_qr_code_data('bag_tag', customer_data, package_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_rooming_list(request, package_id):
    """
    Get rooming list for a package
    
    URL: /api/qr/rooming-list/{package_id}/
    """
    try:
        rooming_data = generate_rooming_list_data(package_id)
        
        return Response({
            'success': True,
            'rooming_data': rooming_data
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def print_rooming_list(request, package_id):
    """
    Generate printable PDF rooming list
    
    URL: /api/qr/rooming-list/{package_id}/print/
    """
    try:
        rooming_data = generate_rooming_list_data(package_id)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        title = Paragraph(f"ROOMING LIST - {rooming_data['package']['name']}", title_style)
        story.append(title)
        
        # Package info
        package_info = f"""
        <b>Package:</b> {rooming_data['package']['name']}<br/>
        <b>Travel Date:</b> {rooming_data['package']['travel_date']}<br/>
        <b>Location:</b> {rooming_data['package']['location']}<br/>
        <b>Total Customers:</b> {rooming_data['total_customers']}<br/>
        <b>Total Rooms:</b> {rooming_data['total_rooms']}
        """
        
        story.append(Paragraph(package_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Room details
        for room_key, room_data in rooming_data['rooms'].items():
            # Room header
            room_header = f"<b>{room_key}</b> ({room_data['room_type']})"
            story.append(Paragraph(room_header, styles['Heading2']))
            
            # Customer table
            table_data = [['Name', 'Booking', 'Type', 'Gender', 'Phone', 'Emergency Contact']]
            
            for customer in room_data['customers']:
                table_data.append([
                    customer['name'],
                    customer['booking_number'],
                    customer['passenger_type'],
                    customer['gender'],
                    customer['phone'],
                    customer['emergency_contact']
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rooming_list_{package_id}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def scan_qr_code(request, qr_type, customer_id):
    """
    Handle QR code scanning - returns customer info
    
    URL: /api/qr/scan/{qr_type}/{customer_id}/
    qr_type: 'id' or 'bag'
    """
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        booking = Booking.objects.filter(customer=customer).first()
        
        if not booking:
            return Response(
                {'error': 'No booking found for this customer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get room info
        room = booking.rooms.first()
        
        scan_data = {
            'scan_type': qr_type,
            'customer': {
                'id': customer.id,
                'name': customer.user.first_name if customer.user else customer.email,
                'email': customer.email,
                'phone': customer.phone
            },
            'booking': {
                'booking_number': booking.booking_number,
                'status': booking.status,
                'package_name': booking.package.name,
                'travel_date': booking.package.travel_date
            },
            'room': {
                'room_number': room.room_number if room else None,
                'hotel_name': room.hotel_name if room else None,
                'room_type': room.sharing_type if room else None
            } if room else None,
            'emergency_contact': {
                'name': booking.emergency_name,
                'phone': booking.emergency_phone,
                'relationship': booking.emergency_relationship
            },
            'scanned_at': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        }
        
        return Response({
            'success': True,
            'data': scan_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_generate_tags(request, package_id):
    """
    Generate ID tags and bag tags for all customers in a package
    
    URL: /api/qr/bulk-tags/{package_id}/
    Body: {"tag_type": "id" or "bag" or "both"}
    """
    try:
        tag_type = request.data.get('tag_type', 'both')
        
        if tag_type not in ['id', 'bag', 'both']:
            return Response(
                {'error': 'tag_type must be "id", "bag", or "both"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        package = get_object_or_404(Package, id=package_id)
        bookings = Booking.objects.filter(package=package).select_related('customer')
        
        results = []
        
        for booking in bookings:
            customer = booking.customer
            
            # Prepare customer data
            customer_data = {
                'id': customer.id,
                'name': customer.user.first_name if customer.user else customer.email,
                'booking_number': booking.booking_number,
                'emergency_contact': f"{booking.emergency_name} - {booking.emergency_phone}",
                'next_of_kin': f"{booking.emergency_name} ({booking.emergency_relationship})"
            }
            
            # Get room info for bag tag
            room = booking.rooms.first()
            if room:
                customer_data.update({
                    'room_number': room.room_number,
                    'hotel_name': room.hotel_name
                })
            
            # Prepare package data
            package_data = {
                'id': package.id,
                'name': package.name,
                'color': getattr(package, 'color', '#2E7D32'),
                'hotel_contact': getattr(package, 'hotel_contact', 'Contact tour leader')
            }
            
            customer_result = {
                'customer_id': customer.id,
                'customer_name': customer_data['name'],
                'booking_number': customer_data['booking_number']
            }
            
            # Generate ID tag
            if tag_type in ['id', 'both']:
                id_tag_base64 = create_id_tag(customer_data, package_data)
                customer_result['id_tag'] = f"data:image/png;base64,{id_tag_base64}"
            
            # Generate bag tag
            if tag_type in ['bag', 'both']:
                bag_tag_base64 = create_bag_tag(customer_data, package_data)
                customer_result['bag_tag'] = f"data:image/png;base64,{bag_tag_base64}"
            
            results.append(customer_result)
        
        return Response({
            'success': True,
            'package_name': package.name,
            'total_customers': len(results),
            'tag_type': tag_type,
            'tags': results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )