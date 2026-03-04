from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = '__all__'

class RoomSharingPriceSerializer(serializers.ModelSerializer):
    sharing_type_display = serializers.CharField(source='get_sharing_type_display', read_only=True)
    
    class Meta:
        model = RoomSharingPrice
        fields = '__all__'

class AddOnSerializer(serializers.ModelSerializer):
    addon_type_display = serializers.CharField(source='get_addon_type_display', read_only=True)
    
    class Meta:
        model = AddOn
        fields = '__all__'

class PackageListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    min_price = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    registered_pax = serializers.SerializerMethodField()
    balance_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = ['id', 'name', 'slug', 'short_description', 'travel_date', 'return_date', 
                  'duration_days', 'duration_nights', 'location', 'featured_image', 
                  'is_featured', 'category_name', 'min_price', 'tags', 'max_capacity', 
                  'registered_pax', 'balance_seats']
    
    def get_min_price(self, obj):
        min_price = obj.room_prices.filter(available=True).order_by('price').first()
        return float(min_price.price) if min_price else 0
    
    def get_registered_pax(self, obj):
        # Count all passengers from confirmed and pending bookings
        try:
            from django.db.models import Q
            bookings = obj.bookings.filter(Q(status='confirmed') | Q(status='pending'))
            total_pax = 0
            for booking in bookings:
                for room in booking.rooms.all():
                    total_pax += room.passengers.count()
            return total_pax
        except Exception as e:
            print(f"Error calculating registered_pax for package {obj.id}: {e}")
            return 0
    
    def get_balance_seats(self, obj):
        try:
            registered = self.get_registered_pax(obj)
            return max(0, obj.max_capacity - registered)
        except Exception as e:
            print(f"Error calculating balance_seats for package {obj.id}: {e}")
            return 0

class PackageDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    room_prices = RoomSharingPriceSerializer(many=True, read_only=True)
    images = PackageImageSerializer(many=True, read_only=True)
    addons = AddOnSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    registered_pax = serializers.SerializerMethodField()
    balance_seats = serializers.SerializerMethodField()
    tour_leader_name = serializers.SerializerMethodField()
    tour_leader_email = serializers.SerializerMethodField()
    tour_leader_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = '__all__'
    
    def get_tour_leader_name(self, obj):
        if obj.tour_leader:
            # Try to get name from user or booking
            if obj.tour_leader.user:
                return f"{obj.tour_leader.user.first_name} {obj.tour_leader.user.last_name}".strip() or obj.tour_leader.email
            # Try to get name from their bookings
            booking = obj.tour_leader.bookings.first()
            if booking:
                return booking.contact_name
            return obj.tour_leader.email
        return None
    
    def get_tour_leader_email(self, obj):
        return obj.tour_leader.email if obj.tour_leader else None
    
    def get_tour_leader_phone(self, obj):
        if obj.tour_leader:
            # Try to get phone from their bookings
            booking = obj.tour_leader.bookings.first()
            if booking:
                return booking.contact_phone
            return obj.tour_leader.phone
        return None
    
    def get_registered_pax(self, obj):
        # Count all passengers from confirmed and pending bookings
        try:
            from django.db.models import Q
            bookings = obj.bookings.filter(Q(status='confirmed') | Q(status='pending'))
            total_pax = 0
            for booking in bookings:
                for room in booking.rooms.all():
                    total_pax += room.passengers.count()
            return total_pax
        except Exception as e:
            print(f"Error calculating registered_pax for package {obj.id}: {e}")
            return 0
    
    def get_balance_seats(self, obj):
        try:
            registered = self.get_registered_pax(obj)
            return max(0, obj.max_capacity - registered)
        except Exception as e:
            print(f"Error calculating balance_seats for package {obj.id}: {e}")
            return 0

class TravelItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = TravelItem
        fields = '__all__'

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'

class BookingRoomSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    
    class Meta:
        model = BookingRoom
        fields = '__all__'

class BookingAddOnSerializer(serializers.ModelSerializer):
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    
    class Meta:
        model = BookingAddOn
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = '__all__'
    
    def get_customer_name(self, obj):
        # Try to get name from booking's contact_name
        if obj.booking:
            return obj.booking.contact_name
        return None

class BookingSerializer(serializers.ModelSerializer):
    rooms = BookingRoomSerializer(many=True, read_only=True)
    booking_addons = BookingAddOnSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def get_display_name(self, obj):
        # Try to get name from user
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            if full_name:
                return full_name
        # Try to get name from their bookings
        booking = obj.bookings.first()
        if booking:
            return booking.contact_name
        return obj.email

class BookingCreateSerializer(serializers.Serializer):
    package_id = serializers.IntegerField()
    rooms = serializers.ListField()
    contact_info = serializers.DictField()
    emergency_contact = serializers.DictField()
    passengers = serializers.ListField()
    addons = serializers.ListField(required=False)
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField()
    payment_screenshot = serializers.FileField(required=False, allow_null=True)

class ItemOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_image = serializers.ImageField(source='item.image', read_only=True)
    
    class Meta:
        model = ItemOrderDetail
        fields = '__all__'

class ItemOrderSerializer(serializers.ModelSerializer):
    items = ItemOrderDetailSerializer(many=True, read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = ItemOrder
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['created_at', 'is_read']


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['times_used', 'created_at']
