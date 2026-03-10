from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .authentication import register, verify_otp, login, request_otp, reset_password, admin_login, update_profile
from .chatbot import chat_with_ai
from .live_audio import start_live_audio, join_live_audio, end_live_audio, get_active_sessions
from .qr_views import (
    generate_id_tag, generate_bag_tag, get_rooming_list, 
    print_rooming_list, scan_qr_code, bulk_generate_tags
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'items', TravelItemViewSet)
router.register(r'tags', TagViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'item-orders', ItemOrderViewSet, basename='item-order')
router.register(r'payments', PaymentViewSet, basename='payment')

# Admin routes
router.register(r'admin/packages', AdminPackageViewSet, basename='admin-package')
router.register(r'admin/categories', AdminCategoryViewSet, basename='admin-category')
router.register(r'admin/items', AdminTravelItemViewSet, basename='admin-item')
router.register(r'admin/users', AdminUserViewSet, basename='admin-user')
router.register(r'admin/customers', AdminCustomerViewSet, basename='admin-customer')

urlpatterns = [
    path('', include(router.urls)),
    path('create-booking/', create_booking, name='create-booking'),
    path('create-item-order/', create_item_order, name='create-item-order'),
    path('contact/', submit_contact_message, name='submit-contact'),
    path('item-orders/', get_customer_item_orders, name='customer-item-orders'),
    path('validate-discount/', validate_discount_code, name='validate-discount'),
    path('bookings/<int:booking_id>/invoice/', get_booking_invoice, name='booking-invoice'),
    path('payments/<int:payment_id>/receipt/', get_payment_receipt, name='payment-receipt'),
    path('chat/', chat_with_ai, name='chat-ai'),
    
    # Package Import/Export
    path('packages/export/', export_packages, name='export-packages'),
    path('packages/import/', import_packages, name='import-packages'),
    path('packages/<int:package_id>/passengers/', get_package_passengers, name='package-passengers'),
    path('packages/<int:package_id>/passengers/export/', export_package_passengers, name='export-package-passengers'),
    
    # Authentication endpoints
    path('auth/register/', register, name='register'),
    path('auth/verify-otp/', verify_otp, name='verify-otp'),
    path('auth/login/', login, name='login'),
    path('auth/request-otp/', request_otp, name='request-otp'),
    path('auth/reset-password/', reset_password, name='reset-password'),
    path('auth/profile/', update_profile, name='update-profile'),
    
    # Admin endpoints
    path('admin/login/', admin_login, name='admin-login'),
    
    # Dua endpoints
    path('duas/', dua_categories_list, name='dua-categories'),
    path('duas/<slug:slug>/', dua_category_detail, name='dua-category-detail'),
    path('duas/<slug:category_slug>/<slug:subcategory_slug>/', dua_subcategory_detail, name='dua-subcategory-detail'),
    
    # Customer Document endpoints
    path('customer-documents/', get_customer_documents, name='customer-documents'),
    path('customer-documents/<int:document_id>/', get_document_detail, name='document-detail'),
    path('customer-documents/upload/', upload_customer_document, name='upload-document'),
    
    # Live Audio endpoints
    path('live-audio/start/', start_live_audio, name='start-live-audio'),
    path('live-audio/join/', join_live_audio, name='join-live-audio'),
    path('live-audio/end/', end_live_audio, name='end-live-audio'),
    path('live-audio/active/', get_active_sessions, name='get-active-sessions'),
    
    # QR Code and Rooming List endpoints
    path('qr/id-tag/<int:customer_id>/', generate_id_tag, name='generate-id-tag'),
    path('qr/bag-tag/<int:customer_id>/', generate_bag_tag, name='generate-bag-tag'),
    path('qr/rooming-list/<int:package_id>/', get_rooming_list, name='get-rooming-list'),
    path('qr/rooming-list/<int:package_id>/print/', print_rooming_list, name='print-rooming-list'),
    path('qr/scan/<str:qr_type>/<int:customer_id>/', scan_qr_code, name='scan-qr-code'),
    path('qr/bulk-tags/<int:package_id>/', bulk_generate_tags, name='bulk-generate-tags'),
]
