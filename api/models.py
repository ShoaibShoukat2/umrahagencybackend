from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    CATEGORY_TYPES = [
        ('umrah', 'Umrah'),
        ('hajj', 'Hajj'),
        ('ziarah', 'Ziarah'),
        ('holiday', 'Holiday'),
        ('item', 'Travel Item'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)  # Changed to URLField for external images
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Package(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    travel_date = models.DateField()
    return_date = models.DateField()
    duration_days = models.IntegerField()
    duration_nights = models.IntegerField()
    
    location = models.CharField(max_length=200)
    itinerary = models.TextField(blank=True)
    inclusions = models.TextField(blank=True)
    exclusions = models.TextField(blank=True)
    complimentary_items = models.TextField(blank=True, help_text='Free gifts/items included with package (e.g., Prayer mat, Zamzam bottle, Ihram set)')
    
    featured_image = models.URLField(max_length=500, blank=True, null=True)  # Changed to URLField for external images
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    min_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    min_deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Child and Infant Pricing (percentage of adult price)
    child_no_bed_price_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100, help_text="Percentage of adult price for child (no bed) (e.g., 100 = 100%)")
    infant_price_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=25, help_text="Percentage of adult price for infants (e.g., 25 = 25%)")
    
    # Capacity tracking
    max_capacity = models.IntegerField(default=50, help_text="Maximum number of passengers for this package")
    
    # Hotel Details
    hotel_name = models.CharField(max_length=300, blank=True, default='', help_text="Name of the hotel")
    hotel_star_rating = models.IntegerField(blank=True, null=True, help_text="Hotel star rating (1-5)")
    hotel_country = models.CharField(max_length=100, blank=True, default='', help_text="Country where hotel is located")
    hotel_image = models.URLField(max_length=500, blank=True, null=True, help_text="Hotel image URL")
    
    # Tour Leader - ForeignKey to Customer marked as tour leader
    tour_leader = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_packages', help_text="Select a customer marked as tour leader")
    
    tags = models.ManyToManyField(Tag, blank=True, related_name='packages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-travel_date', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.travel_date}"

class PackageImage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='images')
    image = models.URLField(max_length=500)  # Changed to URLField for external images
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']

class RoomSharingPrice(models.Model):
    SHARING_TYPES = [
        ('single', 'Single (1 Adult)'),
        ('double', 'Double Sharing (2 Adults)'),
        ('triple', 'Triple Sharing (3 Adults)'),
        ('quad', 'Quad Sharing (4 Adults)'),
    ]
    
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='room_prices')
    sharing_type = models.CharField(max_length=20, choices=SHARING_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    available = models.BooleanField(default=True)
    max_capacity = models.IntegerField(default=50)
    
    class Meta:
        unique_together = ['package', 'sharing_type']
        ordering = ['price']
    
    def __str__(self):
        return f"{self.package.name} - {self.get_sharing_type_display()}: ${self.price}"

class TravelItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', limit_choices_to={'category_type': 'item'})
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    image = models.URLField(max_length=500, blank=True, null=True)  # Changed to URLField for external images
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class AddOn(models.Model):
    ADDON_TYPES = [
        ('room', 'Room Add-on'),
        ('person', 'Person Add-on'),
        ('flight', 'Flight Upgrade'),
        ('other', 'Other'),
    ]
    
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='addons', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    addon_type = models.CharField(max_length=20, choices=ADDON_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    unit_number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    is_tour_leader = models.BooleanField(default=False, help_text='Mark this customer as a tour leader')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    
    booking_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    contact_name = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    contact_address = models.TextField()
    contact_unit = models.CharField(max_length=50, blank=True)
    contact_postal = models.CharField(max_length=20)
    
    emergency_name = models.CharField(max_length=200)
    emergency_phone = models.CharField(max_length=20)
    emergency_relationship = models.CharField(max_length=100)
    
    special_requests = models.TextField(blank=True)
    remarks = models.TextField(blank=True, help_text='Booking remarks for invoice')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.booking_number} - {self.customer.email}"

class BookingRoom(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.IntegerField()
    sharing_type = models.CharField(max_length=20)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    num_adults = models.IntegerField(default=0)
    num_children = models.IntegerField(default=0)
    num_infants = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Room {self.room_number} - {self.booking.booking_number}"

class Passenger(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    PASSENGER_TYPES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]
    
    booking_room = models.ForeignKey(BookingRoom, on_delete=models.CASCADE, related_name='passengers')
    passenger_type = models.CharField(max_length=10, choices=PASSENGER_TYPES)
    
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    passport_number = models.CharField(max_length=50)
    passport_expiry = models.DateField()
    passport_issue_date = models.DateField()
    passport_photo = models.ImageField(upload_to='passports/', blank=True, null=True)
    photo_id = models.ImageField(upload_to='photo_ids/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.passenger_type}"

class BookingAddOn(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_addons', null=True, blank=True)
    booking_room = models.ForeignKey(BookingRoom, on_delete=models.CASCADE, related_name='room_addons', null=True, blank=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='passenger_addons', null=True, blank=True)
    
    addon = models.ForeignKey(AddOn, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.addon.name} - {self.booking.booking_number if self.booking else 'N/A'}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('paynow', 'PayNow'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    
    payment_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_screenshot = models.FileField(upload_to='payment_screenshots/', blank=True, null=True, help_text='Payment proof screenshot (image/PDF) - Cannot be changed once uploaded')
    notes = models.TextField(blank=True)
    remarks = models.TextField(blank=True, help_text='Payment remarks for invoice')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        # Prevent screenshot modification after initial upload
        if self.pk:  # If updating existing payment
            old_payment = Payment.objects.get(pk=self.pk)
            if old_payment.payment_screenshot and self.payment_screenshot != old_payment.payment_screenshot:
                # Restore old screenshot
                self.payment_screenshot = old_payment.payment_screenshot
        super().save(*args, **kwargs)

class ItemOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='item_orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_screenshot = models.FileField(upload_to='order_screenshots/', blank=True, null=True, help_text='Payment proof screenshot (image/PDF) - Cannot be changed once uploaded')
    
    shipping_name = models.CharField(max_length=200, blank=True, default='')
    shipping_address = models.TextField()
    shipping_unit = models.CharField(max_length=50, blank=True)
    shipping_postal = models.CharField(max_length=20)
    shipping_city = models.CharField(max_length=100, blank=True, default='')
    shipping_country = models.CharField(max_length=100, blank=True, default='Singapore')
    shipping_phone = models.CharField(max_length=20, blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        # Prevent screenshot modification after initial upload
        if self.pk:  # If updating existing order
            old_order = ItemOrder.objects.get(pk=self.pk)
            if old_order.payment_screenshot and self.payment_screenshot != old_order.payment_screenshot:
                # Restore old screenshot
                self.payment_screenshot = old_order.payment_screenshot
        super().save(*args, **kwargs)

class ItemOrderDetail(models.Model):
    order = models.ForeignKey(ItemOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(TravelItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"


class DiscountCode(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    times_used = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'}"
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False, "This discount code is not active"
        
        if now < self.valid_from:
            return False, "This discount code is not yet valid"
        
        if now > self.valid_until:
            return False, "This discount code has expired"
        
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "This discount code has reached its usage limit"
        
        return True, "Valid"
    
    def calculate_discount(self, amount):
        if self.discount_type == 'percentage':
            discount = (amount * self.discount_value) / 100
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value
        
        return min(discount, amount)


class DuaCategory(models.Model):
    """Main category for duas (e.g., Umrah, Hajj, Daily Prayers, Travel)"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=100, help_text="Icon name from @expo/vector-icons")
    icon_type = models.CharField(max_length=50, default='MaterialCommunityIcons', help_text="Icon library (MaterialCommunityIcons, Ionicons, FontAwesome5)")
    color = models.CharField(max_length=20, default='#2e7d32', help_text="Hex color code")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Dua Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class DuaSubCategory(models.Model):
    """Sub-category for duas (e.g., Niat, Tawaf, Sa'i, Tahallul)"""
    category = models.ForeignKey(DuaCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    has_rounds = models.BooleanField(default=False, help_text="True if this subcategory has rounds (like Tawaf)")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Dua Sub-Categories'
        ordering = ['order', 'name']
        unique_together = ['category', 'slug']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class DuaRound(models.Model):
    """Rounds for subcategories like Tawaf (First Round, Second Round, etc.)"""
    subcategory = models.ForeignKey(DuaSubCategory, on_delete=models.CASCADE, related_name='rounds')
    name = models.CharField(max_length=200, help_text="e.g., First Round, Second Round")
    round_number = models.IntegerField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'round_number']
        unique_together = ['subcategory', 'round_number']
    
    def __str__(self):
        return f"{self.subcategory.name} - {self.name}"


class Dua(models.Model):
    """Individual dua with Arabic text, transliteration, and translation"""
    subcategory = models.ForeignKey(DuaSubCategory, on_delete=models.CASCADE, related_name='duas', null=True, blank=True)
    round = models.ForeignKey(DuaRound, on_delete=models.CASCADE, related_name='duas', null=True, blank=True, help_text="For duas that belong to a specific round")
    
    title = models.CharField(max_length=300)
    arabic_text = models.TextField(help_text="Arabic text of the dua")
    transliteration = models.TextField(help_text="Romanized pronunciation")
    translation = models.TextField(help_text="English translation")
    description = models.TextField(help_text="Context or when to recite this dua")
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        if self.round:
            return f"{self.round.subcategory.name} - {self.round.name} - {self.title}"
        return f"{self.subcategory.name} - {self.title}"


class CustomerDocument(models.Model):
    """Documents uploaded by staff for customers (e.g., visa, tickets, itinerary)"""
    DOCUMENT_TYPES = [
        ('visa', 'Visa'),
        ('ticket', 'Flight Ticket'),
        ('hotel', 'Hotel Voucher'),
        ('itinerary', 'Travel Itinerary'),
        ('insurance', 'Travel Insurance'),
        ('vaccination', 'Vaccination Certificate'),
        ('passport', 'Passport Copy'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents', null=True, blank=True, help_text="Optional: Link to specific booking")
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200, help_text="Document title (e.g., 'Saudi Visa', 'Flight Ticket - SQ123')")
    description = models.TextField(blank=True, help_text="Additional notes about the document")
    
    file = models.FileField(upload_to='customer_documents/', help_text="Upload PDF, image, or document file")
    file_size = models.IntegerField(blank=True, null=True, help_text="File size in bytes")
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Staff member who uploaded this")
    
    is_important = models.BooleanField(default=False, help_text="Mark as important/urgent document")
    expiry_date = models.DateField(null=True, blank=True, help_text="Document expiry date (if applicable)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_important', '-created_at']
        verbose_name = 'Customer Document'
        verbose_name_plural = 'Customer Documents'
    
    def __str__(self):
        return f"{self.customer.email} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Calculate file size if not set
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class LiveAudioSession(models.Model):
    """
    Live Audio Streaming Session
    Tracks active and past live audio broadcasts by tour leaders
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='live_sessions')
    channel_name = models.CharField(max_length=200, unique=True, help_text='Agora channel name')
    title = models.CharField(max_length=300, default='Live Audio from Tour Leader')
    tour_leader_email = models.EmailField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    listener_count = models.IntegerField(default=0, help_text='Number of customers who joined')
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Live Audio Session'
        verbose_name_plural = 'Live Audio Sessions'
    
    def __str__(self):
        return f"{self.title} - {self.package.name} ({self.status})"
    
    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return None
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        return self.status == 'active'
