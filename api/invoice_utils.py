"""
Invoice and Receipt Generation Utilities
"""
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime
import base64
import os
from django.conf import settings


def get_logo_base64():
    """Convert logo to base64 for embedding in PDF"""
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo.jpeg')
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{logo_data}"
    except Exception as e:
        print(f"Error loading logo: {e}")
        return ""


def generate_invoice_html(booking):
    """
    Generate HTML invoice for a booking - TM Fouzy Format
    """
    logo_base64 = get_logo_base64()
    
    context = {
        'booking': booking,
        'company': {
            'name': 'TM Fouzy Travel & Tours Pte Ltd',
            'uen': '199402129H',
            'address': '390 Victoria St #03-15, Singapore 188061',
            'phone': '+65 6294 8044',
            'email': 'enquiry@tmfouzy.sg',
        },
        'generated_date': datetime.now().strftime('%d/%m/%Y'),
        'logo': logo_base64,
    }
    
    # Get package travel date for payment terms
    travel_date = booking.package.travel_date if booking.package else None
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Invoice - {booking.booking_number}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
                font-size: 12px;
            }}
            .invoice-container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
                align-items: flex-start;
            }}
            .company-logo {{
                flex: 1;
            }}
            .company-name {{
                font-size: 24px;
                font-weight: bold;
                color: #16a34a;
                margin-bottom: 5px;
            }}
            .invoice-info {{
                text-align: right;
                flex: 1;
            }}
            .invoice-title {{
                font-size: 28px;
                font-weight: bold;
                color: #dc2626;
                margin-bottom: 5px;
            }}
            .customer-info {{
                text-align: center;
                margin-bottom: 20px;
                padding: 10px;
                background: #f9fafb;
            }}
            .customer-info p {{
                margin: 3px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            th {{
                background: #f3f4f6;
                padding: 8px;
                text-align: left;
                font-weight: bold;
                border: 1px solid #ddd;
                font-size: 11px;
            }}
            td {{
                padding: 8px;
                border: 1px solid #ddd;
                font-size: 11px;
            }}
            .text-right {{
                text-align: right;
            }}
            .text-center {{
                text-align: center;
            }}
            .item-number {{
                color: #dc2626;
                font-weight: bold;
            }}
            .passenger-name {{
                color: #dc2626;
                font-weight: 500;
            }}
            .totals-table {{
                margin-left: auto;
                width: 300px;
                margin-top: 10px;
            }}
            .totals-table td {{
                border: none;
                padding: 5px;
            }}
            .grand-total {{
                font-weight: bold;
                font-size: 13px;
            }}
            .payment-table {{
                margin-top: 20px;
            }}
            .section-title {{
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
                text-transform: uppercase;
            }}
            .info-section {{
                margin-top: 20px;
                padding: 10px;
                background: #f9fafb;
            }}
            .info-section p {{
                margin: 5px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                font-size: 10px;
                color: #666;
                text-align: center;
            }}
            .remarks {{
                font-style: italic;
                color: #666;
                margin-top: 10px;
            }}
            .company-logo-img {{
                max-width: 80px;
                height: auto;
                margin-bottom: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <!-- Header -->
            <div class="header">
                <div class="company-logo">
                    {f'<img src="{context["logo"]}" class="company-logo-img" alt="TM Fouzy Logo" />' if context['logo'] else ''}
                    <div class="company-name">TM FOUZY</div>
                    <div style="color: #16a34a; font-weight: bold;">TRAVEL & TOURS PTE LTD</div>
                    <div style="font-size: 10px; margin-top: 5px; color: #666;">
                        {context['company']['address']}<br>
                        Tel: {context['company']['phone']}<br>
                        Email: {context['company']['email']}
                    </div>
                </div>
                <div class="invoice-info">
                    <div class="invoice-title">Invoice</div>
                    <p style="margin: 3px 0;"><strong>Ref: #{booking.booking_number}</strong></p>
                    <p style="margin: 3px 0;">Register on: {booking.created_at.strftime('%d/%m/%Y')}</p>
                    <p style="margin: 3px 0;">Package: {booking.package.name if booking.package else 'N/A'}</p>
                </div>
            </div>

            <!-- Customer Info -->
            <div class="customer-info">
                <p><strong>Customer:</strong></p>
                <p><strong>{booking.contact_name}</strong></p>
                <p>{booking.contact_email}</p>
                <p>Hp: {booking.contact_phone}</p>
            </div>

            <!-- Items Table -->
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 60%;">Item</th>
                        <th style="width: 15%;" class="text-center">Qty</th>
                        <th style="width: 20%;" class="text-right">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add room items with passengers
    item_number = 1
    for room in booking.rooms.all():
        room_passengers = room.passengers.all()
        
        html += f"""
                    <tr>
                        <td class="item-number">{item_number}</td>
                        <td>
        """
        
        # List each passenger with passport number
        for passenger in room_passengers:
            html += f"""
                            <span class="passenger-name">{passenger.full_name.upper()}</span> ({passenger.passport_number})<br>
            """
        
        html += f"""
                        </td>
                        <td class="text-center">Adult:{room.num_adults}
        """
        
        if room.num_children > 0:
            html += f"<br>Child:{room.num_children}"
        if room.num_infants > 0:
            html += f"<br>Infant:{room.num_infants}"
        
        html += f"""
                        </td>
                        <td class="text-right"><strong>${room.subtotal}</strong></td>
                    </tr>
        """
        item_number += 1
    
    # Add addons
    if booking.booking_addons.exists():
        html += """
                    <tr>
                        <td colspan="4" style="background: #f9fafb;"><strong>Add-on:</strong></td>
                    </tr>
        """
        for addon in booking.booking_addons.all():
            html += f"""
                    <tr>
                        <td></td>
                        <td>{addon.addon.name} = {addon.quantity} PAX (${addon.price})</td>
                        <td class="text-center"></td>
                        <td class="text-right"><strong>${addon.subtotal}</strong></td>
                    </tr>
            """
    
    html += f"""
                </tbody>
            </table>

            <!-- Totals -->
            <table class="totals-table">
                <tr>
                    <td><strong>Subtotal</strong></td>
                    <td class="text-right"><strong>${booking.total_amount}</strong></td>
                </tr>
                <tr class="grand-total">
                    <td><strong>Grand Total</strong></td>
                    <td class="text-right"><strong>${booking.total_amount}</strong></td>
                </tr>
            </table>

            <!-- Payment Table -->
            <div class="section-title">Receipt</div>
            <table class="payment-table">
                <thead>
                    <tr>
                        <th style="width: 12%;">Date</th>
                        <th style="width: 25%;">Payment From/To</th>
                        <th style="width: 25%;">Remarks</th>
                        <th style="width: 13%;">P.Mode</th>
                        <th style="width: 12%;">Receipt No</th>
                        <th style="width: 13%;" class="text-right">Amount</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if booking.payments.exists():
        for payment in booking.payments.all():
            html += f"""
                    <tr>
                        <td>{payment.created_at.strftime('%d/%m/%Y')}</td>
                        <td>By: {booking.contact_name}</td>
                        <td>{payment.remarks if payment.remarks else ''}</td>
                        <td>{payment.get_payment_method_display()}</td>
                        <td>{payment.payment_number}</td>
                        <td class="text-right"><strong>${payment.amount}</strong></td>
                    </tr>
            """
    else:
        html += """
                    <tr>
                        <td colspan="6" class="text-center" style="color: #999;">No payments recorded yet</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>

            <!-- Payment Summary -->
            <table class="totals-table">
                <tr>
                    <td><strong>Total Paid</strong></td>
                    <td class="text-right" style="color: #16a34a;"><strong>${booking.paid_amount}</strong></td>
                </tr>
                <tr class="grand-total">
                    <td><strong>Balance Payment</strong></td>
                    <td class="text-right" style="color: #dc2626;"><strong>${booking.balance_amount}</strong></td>
                </tr>
            </table>

            <!-- Remarks -->
            {f'<p class="remarks">**Remarks: {booking.remarks}</p>' if booking.remarks else ''}

            <!-- Next of Kin -->
            <div class="info-section">
                <p><strong>NEXT OF KIN INFORMATION</strong></p>
                <p><strong>1: {booking.emergency_name} ({booking.emergency_relationship})</strong></p>
                <p>{booking.emergency_phone}</p>
            </div>

            <!-- Payment Method -->
            <div class="info-section" style="margin-top: 15px;">
                <p><strong>PAYMENT METHOD</strong></p>
                <p>Debit Card</p>
                <p>Paynow: 199402129H</p>
                <p>Cheque:</p>
                <p>TM Fouzy Travel & Tours Pte Ltd</p>
            </div>

            <!-- Terms -->
            <div style="margin-top: 20px; padding: 10px; border: 1px solid #ddd; background: #fffbeb;">
                <p style="margin: 5px 0; font-size: 11px; text-align: center;">
                    <strong>PACKAGE PRICE, FLIGHT, VISA AND ITINERARY ARE SUBJECTED TO CHANGES WITHOUT PRIOR NOTICE.</strong>
                </p>
            </div>

            <div style="margin-top: 10px;">
                <p style="margin: 5px 0; font-size: 11px;"><strong>Payment Terms:</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 11px;">
                    <li>100% of package price & Airfare must be completed before {travel_date.strftime('%d %b %Y') if travel_date else '1 month before travel'}.</li>
                </ul>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>Generated on {context['generated_date']} | Page 1 of 1</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_receipt_html(payment):
    """
    Generate HTML receipt for a payment
    """
    booking = payment.booking
    
    # Check if payment is pending
    is_pending = payment.status == 'pending'
    
    context = {
        'payment': payment,
        'booking': booking,
        'company': {
            'name': 'TM Fouzy Travel & Tours Pte Ltd',
            'uen': '199402129H',
            'address': '390 Victoria St #03-15, Singapore 188061',
            'phone': '+65 6294 8044',
            'email': 'enquiry@tmfouzy.sg',
        },
        'generated_date': datetime.now().strftime('%d %B %Y'),
        'is_pending': is_pending,
    }
    
    # Pending status banner
    pending_banner = ''
    if is_pending:
        pending_banner = """
        <div style="background: #fef3c7; border: 3px solid #f59e0b; border-radius: 8px; padding: 20px; margin-bottom: 30px; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #f59e0b; margin-bottom: 10px;">⏳ PAYMENT PENDING</div>
            <p style="margin: 5px 0; color: #92400e; font-size: 16px;">This receipt is pending until admin verification.</p>
            <p style="margin: 5px 0; color: #92400e; font-size: 14px;">You will receive a confirmed receipt once your payment is approved.</p>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Receipt - {payment.payment_number}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .receipt-container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border: 2px solid {'#f59e0b' if is_pending else '#16a34a'};
                {'opacity: 0.8;' if is_pending else ''}
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 3px solid {'#f59e0b' if is_pending else '#16a34a'};
                padding-bottom: 20px;
            }}
            .company-name {{
                font-size: 24px;
                font-weight: bold;
                color: {'#f59e0b' if is_pending else '#16a34a'};
                margin-bottom: 10px;
            }}
            .receipt-title {{
                font-size: 32px;
                font-weight: bold;
                color: {'#f59e0b' if is_pending else '#16a34a'};
                margin: 20px 0 10px 0;
            }}
            .receipt-number {{
                font-size: 18px;
                color: #666;
                margin-bottom: 5px;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                background: {'#fef3c7' if is_pending else '#dcfce7'};
                color: {'#f59e0b' if is_pending else '#16a34a'};
                border: 2px solid {'#f59e0b' if is_pending else '#16a34a'};
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            .info-label {{
                font-weight: bold;
                color: #666;
            }}
            .amount-box {{
                background: {'#fef3c7' if is_pending else '#f0fdf4'};
                border: 2px solid {'#f59e0b' if is_pending else '#16a34a'};
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 30px 0;
            }}
            .amount-label {{
                font-size: 14px;
                color: #666;
                margin-bottom: 10px;
            }}
            .amount-value {{
                font-size: 48px;
                font-weight: bold;
                color: {'#f59e0b' if is_pending else '#16a34a'};
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            .stamp {{
                margin-top: 30px;
                text-align: right;
                font-style: italic;
                color: {'#f59e0b' if is_pending else '#16a34a'};
            }}
        </style>
    </head>
    <body>
        <div class="receipt-container">
            {pending_banner}
            
            <div class="header">
                <div class="company-name">{context['company']['name']}</div>
                <p style="margin: 5px 0;">UEN: {context['company']['uen']}</p>
                <p style="margin: 5px 0;">{context['company']['address']}</p>
                <p style="margin: 5px 0;">Tel: {context['company']['phone']}</p>
                <div class="receipt-title">RECEIPT</div>
                <div class="receipt-number">#{payment.payment_number}</div>
                <div style="font-size: 14px; color: #666;">{payment.created_at.strftime('%d %B %Y, %I:%M %p')}</div>
                <div class="status-badge">{'⏳ PENDING VERIFICATION' if is_pending else '✓ CONFIRMED'}</div>
            </div>

            <div class="amount-box">
                <div class="amount-label">{'AMOUNT SUBMITTED' if is_pending else 'AMOUNT RECEIVED'}</div>
                <div class="amount-value">${payment.amount}</div>
                {f'<div style="font-size: 14px; color: #92400e; margin-top: 10px;">Awaiting admin approval</div>' if is_pending else ''}
            </div>

            <div class="info-row">
                <span class="info-label">Received From:</span>
                <span>{booking.contact_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Email:</span>
                <span>{booking.contact_email}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Phone:</span>
                <span>{booking.contact_phone}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Booking Reference:</span>
                <span>{booking.booking_number}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Package:</span>
                <span>{booking.package.name if booking.package else 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Payment Method:</span>
                <span>{payment.get_payment_method_display()}</span>
            </div>
            {f'<div class="info-row"><span class="info-label">Transaction ID:</span><span>{payment.transaction_id}</span></div>' if payment.transaction_id else ''}
            
            <div style="margin-top: 30px; padding: 15px; background: #f3f4f6; border-radius: 8px;">
                <h4 style="margin-top: 0;">Payment Summary:</h4>
                <div class="info-row" style="border: none;">
                    <span>Total Booking Amount:</span>
                    <span>${booking.total_amount}</span>
                </div>
                <div class="info-row" style="border: none;">
                    <span>Total Paid (including this):</span>
                    <span style="color: #16a34a; font-weight: bold;">${booking.paid_amount}</span>
                </div>
                <div class="info-row" style="border: none;">
                    <span>Balance Remaining:</span>
                    <span style="color: #dc2626; font-weight: bold;">${booking.balance_amount}</span>
                </div>
            </div>

            <div class="stamp">
                <p style="margin: 5px 0;">{'Pending Verification' if is_pending else 'Authorized Signature'}</p>
                <p style="margin: 5px 0; font-size: 24px; font-weight: bold;">TM Fouzy</p>
            </div>

            <div class="footer">
                <p><strong>{'Payment Submitted - Awaiting Confirmation' if is_pending else 'Thank you for your payment!'}</strong></p>
                {f'<p style="color: #f59e0b; font-weight: bold;">⚠️ This receipt will be confirmed once admin verifies your payment.</p>' if is_pending else ''}
                <p>{'Please check back later for confirmation status.' if is_pending else 'This is a computer-generated receipt and does not require a physical signature.'}</p>
                <p>For any queries, please contact us at enquiry@tmfouzy.sg or call +65 6294 8044</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
