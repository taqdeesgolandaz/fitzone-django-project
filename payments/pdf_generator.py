from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse
import os
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect

class InvoiceGenerator:
    """Generate PDF invoices for payments"""
    
    @staticmethod
    def generate_invoice(payment, membership=None):
        """Generate PDF invoice for a payment"""
        
        # # Check payment status
        # if payment.status != 'success':
        #     return None  # Don't generate PDF for pending/failed payments
        
        # Create buffer for PDF
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E94560'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1A1A2E'),
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        # Story (content) list
        story = []
        
        # Header
        story.append(Paragraph("FitZone Fitness Platform", title_style))
        story.append(Paragraph("Smart Fitness & Membership Management", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Company Details
        company_data = [
            ["", ""],
            ["INVOICE", f"#{payment.invoice_number}"],
            ["Date:", payment.created_at.strftime("%d %B, %Y")],
            ["Transaction ID:", payment.razorpay_payment_id or payment.transaction_id or "N/A"],
        ]
        
        company_table = Table(company_data, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#E94560')),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 1), (1, 1), 14),
        ]))
        story.append(company_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Billing Details
        story.append(Paragraph("Billing Details", heading_style))
        user = payment.user
        user_details = [
            ["Name:", user.full_name or user.username],
            ["Email:", user.email],
            ["Phone:", user.mobile_number or "N/A"],
        ]
        
        user_table = Table(user_details, colWidths=[1.5*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice Items Table
        story.append(Paragraph("Invoice Items", heading_style))
        
        # Get plan details
        plan_name = "Membership Plan"
        amount = float(payment.amount)
        if membership and membership.plan:
            plan_name = membership.plan.name
        
        # Table data
        data = [
            ['Description', 'Quantity', 'Unit Price', 'Total'],
            [plan_name, '1', f'{amount:.2f}', f'{amount:.2f}'],
        ]
        
        items_table = Table(data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E94560')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Payment Information
        story.append(Paragraph("Payment Information", heading_style))
        
        payment_data = [
            ["Payment Method:", payment.payment_method or "Online Payment"],
            ["Payment Status:", "Successful" if payment.status == 'success' else payment.status.title()],
            ["Transaction ID:", payment.razorpay_payment_id or payment.transaction_id or "N/A"],
            ["Transaction Date:", payment.paid_at.strftime("%d %B, %Y %H:%M:%S") if payment.paid_at else payment.created_at.strftime("%d %B, %Y %H:%M:%S")],
        ]
        
        payment_table = Table(payment_data, colWidths=[2*inch, 3.5*inch])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer Note
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#999999'),
            alignment=1
        )
        story.append(Paragraph("Thank you for choosing FitZone! This is a system generated invoice.", note_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    @staticmethod
    def download_invoice(request, payment_id):
        """Download invoice as PDF"""
        from .models import Payment
        from membership.models import UserMembership
        
        payment = Payment.objects.get(id=payment_id)
        
        # # Check if payment is successful before allowing download
        # if payment.status != 'success':
        #     messages.error(request, 'Invoice is only available for successful payments.')
        #     return redirect('payments:payment_history')
        
        membership = UserMembership.objects.filter(payment_id=payment.razorpay_payment_id).first()
        
        # Check permission (user can download their own invoice or admin)
        if request.user != payment.user and not request.user.is_staff:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("You don't have permission to download this invoice.")
        
        # Generate PDF
        pdf_data = InvoiceGenerator.generate_invoice(payment, membership)
        
        if pdf_data is None:
            messages.error(request, 'Invoice not available for pending payments.')
            return redirect('payments:payment_history')
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{payment.invoice_number}.pdf"'
        response.write(pdf_data)
        
        return response