from django.contrib import admin
from .models import BankAccount, Payment

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'account_number', 'account_holder_name', 'is_active', 'is_verified']
    list_filter = ['is_active', 'is_verified', 'bank_name']
    search_fields = ['account_number', 'account_holder_name']
    list_editable = ['is_active', 'is_verified']
    
    fieldsets = (
        ('Bank Details', {
            'fields': ('bank_name', 'branch_name', 'account_holder_name', 'account_number', 'confirm_account_number', 'ifsc_code', 'account_type')
        }),
        ('UPI & Verification', {
            'fields': ('upi_id', 'is_active', 'is_verified', 'pan_number', 'gst_number')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id', 'invoice_number']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'invoice_number']