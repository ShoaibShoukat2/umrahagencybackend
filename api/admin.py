from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import *

# Customize User Admin
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'order', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category_type', 'description')
        }),
        ('Display Settings', {
            'fields': ('image', 'order', 'is_active')
        }),
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'package_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def package_count(self, obj):
        return obj.packages.count()
    package_count.short_description = 'Packages'

class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 1
    fields = ['image', 'caption', 'order']

class RoomSharingPriceInline(admin.TabularInline):
    model = RoomSharingPrice
    extra = 3
    fields = ['sharing_type', 'price', 'available', 'max_capacity']

class AddOnInline(admin.TabularInline):
    model = AddOn
    extra = 1
    fields = ['name', 'addon_type', 'price', 'description', 'is_active']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'travel_date', 'duration_display', 'min_price', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active', 'travel_date', 'created_at']
    search_fields = ['name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags']
    list_editable = ['is_featured', 'is_active']
    date_hierarchy = 'travel_date'
    inlines = [PackageImageInline, RoomSharingPriceInline, AddOnInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'short_description', 'description')
        }),
        ('Travel Details', {
            'fields': ('travel_date', 'return_date', 'duration_days', 'duration_nights', 'location')
        }),
        ('Package Details', {
            'fields': ('itinerary', 'inclusions', 'exclusions', 'complimentary_items', 'tags')
        }),
        ('Pricing', {
            'fields': ('min_deposit_amount', 'min_deposit_percentage', 'child_no_bed_price_percentage', 'infant_price_percentage')
        }),
        ('Media & Status', {
            'fields': ('featured_image', 'is_featured', 'is_active')
        }),
    )
    
    def duration_display(self, obj):
        return f"{obj.duration_days}D/{obj.duration_nights}N"
    duration_display.short_description = 'Duration'
    
    def min_price(self, obj):
        min_price = obj.room_prices.filter(available=True).order_by('price').first()
        if min_price:
            return format_html('<span style="color: green; font-weight: bold;">${}</span>', min_price.price)
        return '-'
    min_price.short_description = 'Min Price'

@admin.register(PackageImage)
class PackageImageAdmin(admin.ModelAdmin):
    list_display = ['package', 'caption', 'order', 'image_preview']
    list_filter = ['package']
    search_fields = ['package__name', 'caption']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'

@admin.register(RoomSharingPrice)
class RoomSharingPriceAdmin(admin.ModelAdmin):
    list_display = ['package', 'sharing_type', 'price', 'available', 'max_capacity']
    list_filter = ['sharing_type', 'available', 'package__category']
    search_fields = ['package__name']
    list_editable = ['price', 'available', 'max_capacity']

@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ['name', 'package', 'addon_type', 'price', 'is_active']
    list_filter = ['addon_type', 'is_active', 'package']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']

@admin.register(TravelItem)
class TravelItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock_quantity', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media & Status', {
            'fields': ('image', 'is_active')
        }),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'postal_code', 'total_bookings', 'total_spent', 'created_at']
    search_fields = ['email', 'phone', 'address']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'total_bookings', 'total_spent']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'email')
        }),
        ('Contact Details', {
            'fields': ('phone', 'address', 'unit_number', 'postal_code')
        }),
        ('Statistics', {
            'fields': ('total_bookings', 'total_spent', 'created_at')
        }),
    )
    
    def total_bookings(self, obj):
        return obj.bookings.count()
    total_bookings.short_description = 'Total Bookings'
    
    def total_spent(self, obj):
        total = sum([booking.paid_amount for booking in obj.bookings.all()])
        return format_html('<span style="color: green; font-weight: bold;">${}</span>', total)
    total_spent.short_description = 'Total Spent'

class BookingRoomInline(admin.TabularInline):
    model = BookingRoom
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['room_number', 'sharing_type', 'num_adults', 'num_children', 'num_infants', 'price_per_person', 'subtotal']

class BookingAddOnInline(admin.TabularInline):
    model = BookingAddOn
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['addon', 'quantity', 'price', 'subtotal']

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_number', 'amount', 'payment_method', 'status', 'created_at']
    can_delete = False

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'customer_email', 'package', 'status', 'total_amount', 'paid_amount', 'balance_amount', 'created_at']
    list_filter = ['status', 'created_at', 'package__category']
    search_fields = ['booking_number', 'customer__email', 'contact_name', 'contact_email']
    readonly_fields = ['booking_number', 'created_at', 'updated_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    inlines = [BookingRoomInline, BookingAddOnInline, PaymentInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_number', 'customer', 'package', 'status')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'paid_amount', 'balance_amount'),
            'classes': ('wide',)
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_phone', 'contact_email', 'contact_address', 'contact_unit', 'contact_postal')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_name', 'emergency_phone', 'emergency_relationship')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'remarks', 'created_at', 'updated_at')
        }),
    )
    
    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer Email'
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = 'Mark selected as Confirmed'
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = 'Mark selected as Completed'
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = 'Mark selected as Cancelled'

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0
    fields = ['full_name', 'passenger_type', 'gender', 'date_of_birth', 'passport_number', 'passport_expiry']

@admin.register(BookingRoom)
class BookingRoomAdmin(admin.ModelAdmin):
    list_display = ['booking', 'room_number', 'sharing_type', 'num_adults', 'num_children', 'num_infants', 'subtotal']
    list_filter = ['sharing_type', 'booking__status']
    search_fields = ['booking__booking_number']
    inlines = [PassengerInline]

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'passenger_type', 'gender', 'date_of_birth', 'passport_number', 'passport_expiry']
    list_filter = ['passenger_type', 'gender']
    search_fields = ['full_name', 'passport_number', 'phone']
    date_hierarchy = 'date_of_birth'

@admin.register(BookingAddOn)
class BookingAddOnAdmin(admin.ModelAdmin):
    list_display = ['booking', 'addon', 'quantity', 'price', 'subtotal']
    list_filter = ['addon__addon_type']
    search_fields = ['booking__booking_number', 'addon__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'booking_number', 'customer_email', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['payment_number', 'transaction_id', 'booking__booking_number', 'customer__email']
    readonly_fields = ['payment_number', 'created_at', 'updated_at', 'get_payment_screenshot_display']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'booking', 'customer', 'amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'transaction_id', 'get_payment_screenshot_display')
        }),
        ('Additional Information', {
            'fields': ('notes', 'remarks', 'created_at', 'updated_at')
        }),
    )
    
    def get_payment_screenshot_display(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<a href="{}" target="_blank">View Screenshot</a><br>'
                '<small style="color: red;">⚠️ Screenshot cannot be changed once uploaded</small>',
                obj.payment_screenshot.url
            )
        return "No screenshot uploaded"
    get_payment_screenshot_display.short_description = 'Payment Screenshot'
    
    def get_readonly_fields(self, request, obj=None):
        # Make payment_screenshot readonly if object exists and has screenshot
        readonly = list(self.readonly_fields)
        if obj and obj.payment_screenshot:
            readonly.append('payment_screenshot')
        return readonly
    
    def booking_number(self, obj):
        return obj.booking.booking_number
    booking_number.short_description = 'Booking #'
    
    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer'
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_as_failed.short_description = 'Mark as Failed'

class ItemOrderDetailInline(admin.TabularInline):
    model = ItemOrderDetail
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['item', 'quantity', 'price', 'subtotal']

@admin.register(ItemOrder)
class ItemOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'get_payment_screenshot_display']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    inlines = [ItemOrderDetailInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_amount', 'get_payment_screenshot_display')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'shipping_unit', 'shipping_postal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_payment_screenshot_display(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<a href="{}" target="_blank">View Screenshot</a><br>'
                '<small style="color: red;">⚠️ Screenshot cannot be changed once uploaded</small>',
                obj.payment_screenshot.url
            )
        return "No screenshot uploaded"
    get_payment_screenshot_display.short_description = 'Payment Screenshot'
    
    def get_readonly_fields(self, request, obj=None):
        # Make payment_screenshot readonly if object exists and has screenshot
        readonly = list(self.readonly_fields)
        if obj and obj.payment_screenshot:
            readonly.append('payment_screenshot')
        return readonly
    
    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = 'Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = 'Mark as Delivered'

@admin.register(ItemOrderDetail)
class ItemOrderDetailAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'item__name']

# Customize Admin Site
admin.site.site_header = "Umrah Agency Admin"
admin.site.site_title = "Umrah Agency Admin Portal"
admin.site.index_title = "Welcome to Umrah Agency Administration"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'subject']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Mark as Read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = 'Mark as Unread'


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'times_used', 'usage_limit', 'valid_from', 'valid_until', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    list_editable = ['is_active']
    readonly_fields = ['times_used', 'created_at']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'is_active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount', 'min_purchase_amount')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'times_used')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


# Dua Admin
@admin.register(DuaCategory)
class DuaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon_name', 'icon_type', 'color', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(DuaSubCategory)
class DuaSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'has_rounds', 'order', 'is_active']
    list_filter = ['category', 'has_rounds', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category', 'order', 'name']


@admin.register(DuaRound)
class DuaRoundAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory', 'round_number', 'order', 'is_active']
    list_filter = ['subcategory', 'is_active']
    search_fields = ['name']
    ordering = ['subcategory', 'order', 'round_number']


@admin.register(Dua)
class DuaAdmin(admin.ModelAdmin):
    list_display = ['title', 'subcategory', 'round', 'order', 'is_active']
    list_filter = ['subcategory', 'round', 'is_active']
    search_fields = ['title', 'arabic_text', 'transliteration', 'translation', 'description']
    ordering = ['subcategory', 'round', 'order']
    fieldsets = (
        ('Basic Information', {
            'fields': ('subcategory', 'round', 'title', 'description')
        }),
        ('Dua Content', {
            'fields': ('arabic_text', 'transliteration', 'translation')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )


# Customer Document Admin
@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'document_type', 'booking', 'is_important', 'expiry_date', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'is_important', 'created_at', 'expiry_date']
    search_fields = ['title', 'description', 'customer__email', 'customer__user__username']
    readonly_fields = ['file_size', 'created_at', 'updated_at']
    autocomplete_fields = ['customer', 'booking', 'uploaded_by']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('customer', 'booking', 'document_type', 'title', 'description')
        }),
        ('File', {
            'fields': ('file', 'file_size')
        }),
        ('Settings', {
            'fields': ('is_important', 'expiry_date', 'uploaded_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Automatically set uploaded_by to current user if not set
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'booking', 'uploaded_by')
