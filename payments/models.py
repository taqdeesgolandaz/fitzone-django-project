from django.db import models
from django.conf import settings

class BankAccount(models.Model):
    """Store business bank account details for payments"""
    
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20, unique=True)
    confirm_account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=200, blank=True)
    upi_id = models.CharField(max_length=100, blank=True, help_text="UPI ID for payments")
    
    # Account type
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='current')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Additional info
    pan_number = models.CharField(max_length=10, blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number[-4:]}"
    
    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'


class Payment(models.Model):
    """Store payment transactions"""
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    membership = models.ForeignKey('membership.UserMembership', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    
    # Razorpay details
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    # Bank account used
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.user.username} - ₹{self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import uuid
            self.invoice_number = f"INV-{self.user.id}-{uuid.uuid4().hex[:8].upper()}"
        if not self.transaction_id and self.razorpay_payment_id:
            self.transaction_id = self.razorpay_payment_id
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'