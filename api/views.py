from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min
from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid
from .models import *
from .serializers import *

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PackageListSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['travel_date', 'created_at']
    
    def get_queryset(self):
        queryset = Package.objects.filter(is_active=True).prefetch_related('room_prices', 'tags')
        
        # Filter by month
        month = self.request.query_params.get('month', None)
        if month:
            try:
                month_num = int(month)
                queryset = queryset.filter(travel_date__month=month_num)
            except ValueError:
                pass
        
        # Filter by year
        year = self.request.query_params.get('year', None)
        if year:
            try:
                year_num = int(year)
                queryset = queryset.filter(travel_date__year=year_num)
            except ValueError:
                pass
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price or max_price:
            price_filter = Q()
            if min_price:
                price_filter &= Q(room_prices__price__gte=min_price)
            if max_price:
                price_filter &= Q(room_prices__price__lte=max_price)
            queryset = queryset.filter(price_filter).distinct()
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__slug__in=tag_list).distinct()
        
        # Featured packages
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PackageDetailSerializer
        return PackageListSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        packages = Package.objects.filter(is_active=True, is_featured=True)[:6]
        serializer = self.get_serializer(packages, many=True)
        return Response(serializer.data)

class TravelItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TravelItem.objects.filter(is_active=True)
    serializer_class = TravelItemSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category__slug']
    search_fields = ['name', 'description']

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'

@api_view(['POST'])
def create_booking(request):
    from django.db import transaction
    
    try:
        with transaction.atomic():
            import json
            data = request.data.copy()
            
            print("=== CREATE BOOKING DEBUG ===")
            print(f"Raw data keys: {data.keys()}")
            
            # Parse JSON fields if they come as strings (from FormData)
            if isinstance(data.get('rooms'), str):
                data['rooms'] = json.loads(data['rooms'])
            if isinstance(data.get('contact_info'), str):
                data['contact_info'] = json.loads(data['contact_info'])
            if isinstance(data.get('emergency_contact'), str):
                data['emergency_contact'] = json.loads(data['emergency_contact'])
            if isinstance(data.get('passengers'), str):
                data['passengers'] = json.loads(data['passengers'])
            if isinstance(data.get('addons'), str):
                data['addons'] = json.loads(data['addons'])
            
            print(f"Rooms: {len(data.get('rooms', []))}")
            print(f"Passengers: {len(data.get('passengers', []))}")
            print(f"Addons: {len(data.get('addons', []))}")
            
            # Get or create customer
            customer_email = data['contact_info']['email']
            customer, created = Customer.objects.get_or_create(
                email=customer_email,
                defaults={
                    'phone': data['contact_info']['phone'],
                    'address': data['contact_info'].get('address', ''),
                    'unit_number': data['contact_info'].get('unit', ''),
                    'postal_code': data['contact_info'].get('postal_code', '')
                }
            )
            
            print(f"Customer: {customer.email} (created: {created})")
            
            # Get package
            package = Package.objects.get(id=data['package_id'])
            print(f"Package: {package.name}")
            
            # Create booking
            booking_number = f"BK{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            booking = Booking.objects.create(
                customer=customer,
                package=package,
                booking_number=booking_number,
                contact_name=data['contact_info']['name'],
                contact_phone=data['contact_info']['phone'],
                contact_email=data['contact_info']['email'],
                contact_address=data['contact_info'].get('address', ''),
                contact_unit=data['contact_info'].get('unit', ''),
                contact_postal=data['contact_info'].get('postal_code', ''),
                emergency_name=data['emergency_contact']['name'],
                emergency_phone=data['emergency_contact']['phone'],
                emergency_relationship=data['emergency_contact']['relationship'],
                special_requests=data.get('special_requests', '')
            )
            
            print(f"Booking created: {booking.booking_number}")
            
            total_amount = Decimal('0')
        
        # Create rooms and passengers
        for room_index, room_data in enumerate(data['rooms']):
            print(f"Processing room: {room_data}")
            
            room_price = RoomSharingPrice.objects.get(
                package=package,
                sharing_type=room_data['sharing_type']
            )
            
            print(f"Room price found: {room_price.price} for {room_price.sharing_type}")
            
            # Handle missing keys with defaults
            num_adults = room_data.get('num_adults', 0)
            num_children = room_data.get('num_children', 0)
            num_infants = room_data.get('num_infants', 0)
            
            num_people = num_adults + num_children + num_infants
            room_subtotal = Decimal(str(room_price.price)) * num_people
            
            print(f"Room subtotal: {room_subtotal} ({num_people} people: {num_adults} adults, {num_children} children, {num_infants} infants)")
            
            booking_room = BookingRoom.objects.create(
                booking=booking,
                room_number=room_data.get('room_number', room_index + 1),  # Auto-generate if not provided
                sharing_type=room_data['sharing_type'],
                price_per_person=room_price.price,
                num_adults=num_adults,
                num_children=num_children,
                num_infants=num_infants,
                subtotal=room_subtotal
            )
            
            print(f"Room created: {booking_room.id}")
            
            total_amount += room_subtotal
            
            # Create passengers for this room
            # For admin walk-in bookings, all passengers go to the first room
            # For multi-room bookings from frontend, filter by room_number
            if 'room_number' in room_data:
                room_passengers = [p for p in data['passengers'] if p.get('room_number') == room_data['room_number']]
            else:
                # Admin booking: assign all passengers to this room
                room_passengers = data['passengers'] if room_index == 0 else []
            
            print(f"Creating {len(room_passengers)} passengers for room {room_index + 1}")
            
            for idx, passenger_data in enumerate(room_passengers):
                # Find the index in the original passengers list
                passenger_index = next((i for i, p in enumerate(data['passengers']) if p == passenger_data), None)
                
                # Get passport photo and photo ID from FILES
                passport_photo_key = f'passenger_{passenger_index}_passport_photo'
                photo_id_key = f'passenger_{passenger_index}_photo_id'
                
                passport_photo = request.FILES.get(passport_photo_key, None)
                photo_id = request.FILES.get(photo_id_key, None)
                
                passenger = Passenger.objects.create(
                    booking_room=booking_room,
                    passenger_type=passenger_data.get('type', 'adult'),
                    full_name=passenger_data.get('name', passenger_data.get('full_name', '')),
                    phone=passenger_data.get('phone', ''),
                    date_of_birth=passenger_data.get('dob', passenger_data.get('date_of_birth', '')),
                    gender=passenger_data.get('gender', 'male'),
                    passport_number=passenger_data.get('passport_number', ''),
                    passport_expiry=passenger_data.get('passport_expiry', ''),
                    passport_issue_date=passenger_data.get('passport_issue', passenger_data.get('passport_issue_date', '')),
                    passport_photo=passport_photo,
                    photo_id=photo_id
                )
                
                print(f"Passenger created: {passenger.full_name}")
        
        print(f"Total after rooms: {total_amount}")
        
        # Add addons if any
        if 'addons' in data and data['addons']:
            print(f"Processing {len(data['addons'])} addons")
            for addon_data in data['addons']:
                addon = AddOn.objects.get(id=addon_data['addon_id'])
                addon_subtotal = Decimal(str(addon.price)) * addon_data['quantity']
                
                BookingAddOn.objects.create(
                    booking=booking if addon_data.get('applies_to') == 'booking' else None,
                    booking_room=BookingRoom.objects.get(id=addon_data.get('room_id')) if addon_data.get('room_id') else None,
                    passenger=Passenger.objects.get(id=addon_data.get('passenger_id')) if addon_data.get('passenger_id') else None,
                    addon=addon,
                    quantity=addon_data['quantity'],
                    price=addon.price,
                    subtotal=addon_subtotal
                )
                
                total_amount += addon_subtotal
                print(f"Addon added: {addon.name}, subtotal: {addon_subtotal}")
        
        print(f"Total after addons: {total_amount}")
        
        # Handle discount code if provided
        discount_code_obj = None
        if data.get('discount_code'):
            try:
                discount_code_obj = DiscountCode.objects.get(code=data['discount_code'].upper())
                # Increment usage count
                discount_code_obj.times_used += 1
                discount_code_obj.save()
                print(f"Discount code applied: {discount_code_obj.code}")
            except DiscountCode.DoesNotExist:
                print(f"Discount code not found: {data.get('discount_code')}")
                pass  # Ignore if code doesn't exist
        
        # Update booking totals
        booking.total_amount = total_amount
        booking.balance_amount = total_amount
        booking.save()
        
        print(f"Total amount calculated: {total_amount}")
        
        # Create payment
        payment_number = f"PAY{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        payment_amount = Decimal(str(data['payment_amount']))
        payment_screenshot = request.FILES.get('payment_screenshot', None)
        
        print(f"Creating payment: {payment_amount}")
        
        payment = Payment.objects.create(
            booking=booking,
            customer=customer,
            payment_number=payment_number,
            amount=payment_amount,
            payment_method=data['payment_method'],
            payment_screenshot=payment_screenshot,
            status='pending'  # Changed from 'completed' to 'pending' - admin must approve
        )
        
        print(f"Payment created: {payment.payment_number}")
        
        # Don't update booking amounts yet - wait for admin approval
        # booking.paid_amount = payment_amount
        # booking.balance_amount = total_amount - payment_amount
        booking.status = 'pending'  # Keep booking as pending until payment approved
        booking.save()
        
        print(f"Booking complete: Total={booking.total_amount}, Paid={booking.paid_amount}, Balance={booking.balance_amount}")
        print("=== END DEBUG ===")
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        print(f"ERROR in create_booking: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        if email:
            return Booking.objects.filter(customer__email=email).order_by('-created_at')
        # For admin: return all bookings if no email filter
        return Booking.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Admin action to update booking status"""
        try:
            booking = self.get_object()
            new_status = request.data.get('status')
            
            if not new_status:
                return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            booking.status = new_status
            booking.save()
            
            serializer = BookingSerializer(booking)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        try:
            booking = self.get_object()
            amount = request.data.get('amount')
            payment_method = request.data.get('payment_method')
            payment_screenshot = request.FILES.get('payment_screenshot', None)
            
            # Validate required fields
            if not amount:
                return Response({
                    'error': 'Payment amount is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not payment_method:
                return Response({
                    'error': 'Payment method is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate amount
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    return Response({
                        'error': 'Payment amount must be greater than zero'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if amount_decimal > booking.balance_amount:
                    return Response({
                        'error': f'Payment amount cannot exceed balance amount of ${booking.balance_amount}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, InvalidOperation) as e:
                return Response({
                    'error': f'Invalid payment amount: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate payment screenshot for PayNow
            if payment_method == 'paynow' and not payment_screenshot:
                return Response({
                    'error': 'Payment screenshot is required for PayNow payments'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            payment_number = f"PAY{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            payment = Payment.objects.create(
                booking=booking,
                customer=booking.customer,
                payment_number=payment_number,
                amount=amount_decimal,
                payment_method=payment_method,
                payment_screenshot=payment_screenshot,
                status='pending'
            )
            
            # Don't add to paid_amount yet - wait for admin approval
            # booking.paid_amount += amount_decimal
            # booking.balance_amount = booking.total_amount - booking.paid_amount
            # if booking.paid_amount >= booking.total_amount:
            #     booking.status = 'confirmed'
            # booking.save()
            
            serializer = BookingSerializer(booking)
            return Response(serializer.data)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in add_payment: {error_details}")
            return Response({
                'error': f'Payment processing failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        if email:
            return Customer.objects.filter(email=email)
        return Customer.objects.none()


class ItemOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemOrderSerializer
    
    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        if email:
            return ItemOrder.objects.filter(customer__email=email).order_by('-created_at')
        # For admin: return all orders if no email filter
        return ItemOrder.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Admin action to update order status"""
        try:
            order = self.get_object()
            new_status = request.data.get('status')
            
            if not new_status:
                return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            order.status = new_status
            order.save()
            
            serializer = ItemOrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def submit_contact_message(request):
    """
    Submit a contact form message
    """
    try:
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Thank you for contacting us! We will get back to you soon.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_customer_item_orders(request):
    """
    Get all item orders for a customer by email
    """
    email = request.query_params.get('email')
    if not email:
        return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        customer = Customer.objects.get(email=email)
        orders = ItemOrder.objects.filter(customer=customer).order_by('-created_at')
        serializer = ItemOrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_item_order(request):
    """
    Create a new item order
    """
    try:
        import json
        data = request.data.copy()
        
        # Parse JSON fields if they come as strings
        if isinstance(data.get('items'), str):
            data['items'] = json.loads(data['items'])
        
        # Get or create customer
        customer_email = data['customer_email']
        customer = Customer.objects.filter(email=customer_email).first()
        
        if not customer:
            # Auto-create customer from Django user if exists
            from django.contrib.auth.models import User as DjangoUser
            try:
                django_user = DjangoUser.objects.get(username=customer_email)
                customer = Customer.objects.create(
                    user=django_user,
                    email=customer_email,
                    phone=data.get('shipping_phone', ''),
                    address=data.get('shipping_address', '')
                )
            except DjangoUser.DoesNotExist:
                return Response({'error': 'Customer not found. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle discount code if provided
        discount_code_obj = None
        if data.get('discount_code'):
            try:
                discount_code_obj = DiscountCode.objects.get(code=data['discount_code'].upper())
                # Increment usage count
                discount_code_obj.times_used += 1
                discount_code_obj.save()
            except DiscountCode.DoesNotExist:
                pass  # Ignore if code doesn't exist
        
        # Create order
        order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        payment_screenshot = request.FILES.get('payment_screenshot', None)
        
        item_order = ItemOrder.objects.create(
            customer=customer,
            order_number=order_number,
            total_amount=data['total_amount'],
            shipping_address=data['shipping_address'],
            shipping_unit=data.get('shipping_unit', ''),
            shipping_postal=data['shipping_postal'],
            shipping_name=data.get('shipping_name', ''),
            shipping_phone=data.get('shipping_phone', ''),
            shipping_city=data.get('shipping_city', ''),
            shipping_country=data.get('shipping_country', ''),
            payment_screenshot=payment_screenshot,
            status='pending'
        )
        
        # Create order details
        for item_data in data['items']:
            item = TravelItem.objects.get(id=item_data['item_id'])
            subtotal = float(item_data['price']) * item_data['quantity']
            
            ItemOrderDetail.objects.create(
                order=item_order,
                item=item,
                quantity=item_data['quantity'],
                price=item_data['price'],
                subtotal=subtotal
            )
        
        serializer = ItemOrderSerializer(item_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def validate_discount_code(request):
    """
    Validate a discount code and return discount details
    """
    code = request.data.get('code')
    amount = request.data.get('amount')
    
    if not code or not amount:
        return Response({'error': 'Code and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        discount_code = DiscountCode.objects.get(code=code.upper())
        is_valid, message = discount_code.is_valid()
        
        if not is_valid:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        amount = float(amount)
        
        if amount < float(discount_code.min_purchase_amount):
            return Response({
                'error': f'Minimum purchase amount is ${discount_code.min_purchase_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        discount_amount = discount_code.calculate_discount(amount)
        
        return Response({
            'valid': True,
            'code': discount_code.code,
            'discount_type': discount_code.discount_type,
            'discount_value': discount_code.discount_value,
            'discount_amount': discount_amount,
            'final_amount': amount - discount_amount
        })
        
    except DiscountCode.DoesNotExist:
        return Response({'error': 'Invalid discount code'}, status=status.HTTP_400_BAD_REQUEST)


# Invoice and Receipt Views
from django.http import HttpResponse
from .invoice_utils import generate_invoice_html, generate_receipt_html
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
from datetime import datetime

@api_view(['GET'])
def get_booking_invoice(request, booking_id):
    """
    Generate and return invoice PDF for a booking using ReportLab
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # Check if user has access to this booking
        email = request.GET.get('email')
        if not email or booking.customer.email != email:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4A148C'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#6A1B9A'),
            spaceAfter=12,
        )
        
        # Title
        elements.append(Paragraph("BOOKING INVOICE", title_style))
        elements.append(Spacer(1, 12))
        
        # Company Info
        company_data = [
            ['TM Fouzy Travel & Tours'],
            ['Phone: +65 6294 8044'],
            ['Email: enquiry@tmfouzy.sg'],
            ['WhatsApp: +65 9820 1134'],
        ]
        company_table = Table(company_data, colWidths=[5*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 20))
        
        # Booking Details
        elements.append(Paragraph("Booking Information", heading_style))
        booking_data = [
            ['Booking Number:', booking.booking_number],
            ['Package:', booking.package.name if booking.package else 'N/A'],
            ['Customer:', booking.contact_name],
            ['Email:', booking.contact_email],
            ['Phone:', booking.contact_phone],
            ['Booking Date:', booking.created_at.strftime('%d %B %Y')],
            ['Status:', booking.status.upper()],
        ]
        booking_table = Table(booking_data, colWidths=[2*inch, 4*inch])
        booking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3E5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(booking_table)
        elements.append(Spacer(1, 20))
        
        # Passengers
        if booking.rooms.exists():
            elements.append(Paragraph("Passenger Details", heading_style))
            passenger_data = [['#', 'Name', 'Type', 'Passport', 'DOB']]
            idx = 1
            for room in booking.rooms.all():
                for passenger in room.passengers.all():
                    passenger_data.append([
                        str(idx),
                        passenger.full_name,
                        passenger.passenger_type.title(),
                        passenger.passport_number,
                        passenger.date_of_birth.strftime('%d/%m/%Y')
                    ])
                    idx += 1
            
            passenger_table = Table(passenger_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1.5*inch, 1*inch])
            passenger_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6A1B9A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3E5F5')]),
            ]))
            elements.append(passenger_table)
            elements.append(Spacer(1, 20))
        
        # Financial Summary
        elements.append(Paragraph("Payment Summary", heading_style))
        financial_data = [
            ['Total Amount:', f'${booking.total_amount}'],
            ['Paid Amount:', f'${booking.paid_amount}'],
            ['Balance Amount:', f'${booking.balance_amount}'],
        ]
        financial_table = Table(financial_data, colWidths=[4*inch, 2*inch])
        financial_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#D32F2F') if booking.balance_amount > 0 else colors.HexColor('#388E3C')),
        ]))
        elements.append(financial_table)
        elements.append(Spacer(1, 30))
        
        # Footer
        footer_text = "Thank you for choosing TM Fouzy Travel & Tours. May Allah accept your journey."
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey)))
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Invoice_{booking.booking_number}.pdf"'
        return response
        
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_payment_receipt(request, payment_id):
    """
    Generate and return receipt PDF for a payment using ReportLab
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Check if user has access to this payment
        email = request.GET.get('email')
        if not email or payment.customer.email != email:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=12,
        )
        
        # Title
        elements.append(Paragraph("PAYMENT RECEIPT", title_style))
        elements.append(Spacer(1, 12))
        
        # Company Info
        company_data = [
            ['TM Fouzy Travel & Tours'],
            ['Phone: +65 6294 8044'],
            ['Email: enquiry@tmfouzy.sg'],
            ['WhatsApp: +65 9820 1134'],
        ]
        company_table = Table(company_data, colWidths=[5*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 20))
        
        # Payment Details
        elements.append(Paragraph("Payment Information", heading_style))
        payment_data = [
            ['Receipt Number:', payment.payment_number],
            ['Booking Number:', payment.booking.booking_number],
            ['Customer:', payment.customer.email],
            ['Payment Date:', payment.created_at.strftime('%d %B %Y')],
            ['Payment Method:', payment.get_payment_method_display()],
            ['Status:', payment.status.upper()],
        ]
        payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 30))
        
        # Amount
        amount_data = [
            ['Amount Paid:', f'${payment.amount}'],
        ]
        amount_table = Table(amount_data, colWidths=[4*inch, 2*inch])
        amount_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#2E7D32')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#2E7D32')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(amount_table)
        elements.append(Spacer(1, 30))
        
        # Remarks
        if payment.remarks:
            elements.append(Paragraph("Remarks", heading_style))
            elements.append(Paragraph(payment.remarks, styles['Normal']))
            elements.append(Spacer(1, 20))
        
        # Footer
        footer_text = "This is a computer-generated receipt. Thank you for your payment."
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey, fontSize=9)))
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Receipt_{payment.payment_number}.pdf"'
        return response
        
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin CRUD ViewSets
class AdminPackageViewSet(viewsets.ModelViewSet):
    """Admin viewset for full CRUD on packages"""
    queryset = Package.objects.all()
    serializer_class = PackageDetailSerializer
    
    def get_permissions(self):
        # Add permission check for admin users
        return []
    
class AdminCategoryViewSet(viewsets.ModelViewSet):
    """Admin viewset for full CRUD on categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class AdminTravelItemViewSet(viewsets.ModelViewSet):
    """Admin viewset for full CRUD on travel items"""
    queryset = TravelItem.objects.all()
    serializer_class = TravelItemSerializer
    
class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin viewset for user management"""
    from django.contrib.auth.models import User
    from rest_framework import serializers
    
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
            extra_kwargs = {'password': {'write_only': True}}
        
        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user
    
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AdminCustomerViewSet(viewsets.ModelViewSet):
    """Admin viewset for customer management including tour leader assignment"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['get'])
    def tour_leaders(self, request):
        """Get all customers marked as tour leaders"""
        tour_leaders = Customer.objects.filter(is_tour_leader=True)
        serializer = self.get_serializer(tour_leaders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_tour_leader(self, request, pk=None):
        """Toggle tour leader status for a customer"""
        customer = self.get_object()
        customer.is_tour_leader = not customer.is_tour_leader
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)


# Package Import/Export
@api_view(['GET'])
def export_packages(request):
    """Export all packages to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="packages_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Slug', 'Category', 'Location', 'Travel Date', 'Return Date', 
                     'Duration Days', 'Duration Nights', 'Description', 'Short Description',
                     'Featured Image', 'Is Featured', 'Is Active', 'Min Deposit Amount'])
    
    packages = Package.objects.all()
    for pkg in packages:
        writer.writerow([
            pkg.name, pkg.slug, pkg.category.name, pkg.location,
            pkg.travel_date, pkg.return_date, pkg.duration_days, pkg.duration_nights,
            pkg.description, pkg.short_description, pkg.featured_image,
            pkg.is_featured, pkg.is_active, pkg.min_deposit_amount
        ])
    
    return response

@api_view(['POST'])
def import_packages(request):
    """Import packages from CSV"""
    import csv
    import io
    
    try:
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            category = Category.objects.filter(name=row['Category']).first()
            if not category:
                continue
                
            Package.objects.create(
                name=row['Name'],
                slug=row['Slug'],
                category=category,
                location=row['Location'],
                travel_date=row['Travel Date'],
                return_date=row['Return Date'],
                duration_days=int(row['Duration Days']),
                duration_nights=int(row['Duration Nights']),
                description=row['Description'],
                short_description=row.get('Short Description', ''),
                featured_image=row.get('Featured Image', ''),
                is_featured=row.get('Is Featured', 'False') == 'True',
                is_active=row.get('Is Active', 'True') == 'True',
                min_deposit_amount=float(row.get('Min Deposit Amount', 100))
            )
            created_count += 1
        
        return Response({'message': f'Successfully imported {created_count} packages'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_package_passengers(request, package_id):
    """Get all passengers/customers for a specific package"""
    try:
        package = Package.objects.get(id=package_id)
        bookings = Booking.objects.filter(package=package).prefetch_related('rooms__passengers')
        
        passengers_data = []
        for booking in bookings:
            for room in booking.rooms.all():
                for passenger in room.passengers.all():
                    passengers_data.append({
                        'booking_number': booking.booking_number,
                        'full_name': passenger.full_name,
                        'date_of_birth': passenger.date_of_birth,
                        'phone': passenger.phone,
                        'passport_number': passenger.passport_number,
                        'passport_expiry': passenger.passport_expiry,
                        'passport_issue_date': passenger.passport_issue_date,
                        'passenger_type': passenger.passenger_type,
                        'gender': passenger.gender,
                    })
        
        return Response({
            'package_name': package.name,
            'total_passengers': len(passengers_data),
            'passengers': passengers_data
        })
    except Package.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def export_package_passengers(request, package_id):
    """Export passengers list for a package to CSV"""
    import csv
    from django.http import HttpResponse
    
    try:
        package = Package.objects.get(id=package_id)
        bookings = Booking.objects.filter(package=package).prefetch_related('rooms__passengers')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="passengers_{package.slug}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Booking #', 'Full Name', 'Date of Birth', 'Phone', 'Passport Number', 
                        'Passport Expiry', 'Passport Issue Date', 'Type', 'Gender'])
        
        for booking in bookings:
            for room in booking.rooms.all():
                for passenger in room.passengers.all():
                    writer.writerow([
                        booking.booking_number,
                        passenger.full_name,
                        passenger.date_of_birth,
                        passenger.phone,
                        passenger.passport_number,
                        passenger.passport_expiry,
                        passenger.passport_issue_date,
                        passenger.passenger_type,
                        passenger.gender,
                    ])
        
        return response
    except Package.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments"""
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update payment status (accept/reject)"""
        try:
            payment = self.get_object()
            new_status = request.data.get('status')
            
            if not new_status:
                return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            valid_statuses = ['pending', 'completed', 'rejected']
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            old_status = payment.status
            payment.status = new_status
            payment.save()
            
            # Update booking paid amount based on payment status
            booking = payment.booking
            if old_status == 'pending' and new_status == 'completed':
                # Payment accepted - add to paid_amount
                booking.paid_amount += payment.amount
                booking.balance_amount = booking.total_amount - booking.paid_amount
                if booking.paid_amount >= booking.total_amount:
                    booking.status = 'confirmed'
                booking.save()
            elif old_status == 'completed' and new_status == 'rejected':
                # Payment rejected after being accepted - subtract from paid_amount
                booking.paid_amount -= payment.amount
                booking.balance_amount = booking.total_amount - booking.paid_amount
                booking.save()
            elif old_status == 'pending' and new_status == 'rejected':
                # Payment rejected from pending - no change to paid_amount
                pass
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Dua Views
@api_view(['GET'])
def dua_categories_list(request):
    """Get all dua categories with their subcategories and duas"""
    categories = DuaCategory.objects.filter(is_active=True).prefetch_related(
        'subcategories__duas',
        'subcategories__rounds__duas'
    )
    serializer = DuaCategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def dua_category_detail(request, slug):
    """Get a specific dua category with all its subcategories and duas"""
    try:
        category = DuaCategory.objects.prefetch_related(
            'subcategories__duas',
            'subcategories__rounds__duas'
        ).get(slug=slug, is_active=True)
        serializer = DuaCategorySerializer(category)
        return Response(serializer.data)
    except DuaCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=404)


@api_view(['GET'])
def dua_subcategory_detail(request, category_slug, subcategory_slug):
    """Get a specific dua subcategory with its duas or rounds"""
    try:
        subcategory = DuaSubCategory.objects.prefetch_related(
            'duas',
            'rounds__duas'
        ).get(
            category__slug=category_slug,
            slug=subcategory_slug,
            is_active=True
        )
        serializer = DuaSubCategorySerializer(subcategory)
        return Response(serializer.data)
    except DuaSubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=404)


# Customer Document Views
@api_view(['GET'])
def get_customer_documents(request):
    """Get all documents for the logged-in customer"""
    try:
        # Get email from query params or authenticated user
        email = request.query_params.get('email')
        if not email:
            if request.user.is_authenticated:
                email = request.user.email
            else:
                return Response({'error': 'Email parameter required or user must be authenticated'}, status=400)
        
        customer = Customer.objects.get(email=email)
        
        documents = CustomerDocument.objects.filter(customer=customer).select_related(
            'booking', 'uploaded_by'
        )
        
        serializer = CustomerDocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_document_detail(request, document_id):
    """Get details of a specific document"""
    try:
        # Get email from query params or authenticated user
        email = request.query_params.get('email')
        if not email:
            if request.user.is_authenticated:
                email = request.user.email
            else:
                return Response({'error': 'Email parameter required or user must be authenticated'}, status=400)
        
        customer = Customer.objects.get(email=email)
        
        document = CustomerDocument.objects.select_related(
            'booking', 'uploaded_by'
        ).get(id=document_id, customer=customer)
        
        serializer = CustomerDocumentSerializer(document, context={'request': request})
        return Response(serializer.data)
    except CustomerDocument.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def upload_customer_document(request):
    """Upload a document for a customer (staff only)"""
    serializer = CustomerDocumentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Set uploaded_by to current user
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
