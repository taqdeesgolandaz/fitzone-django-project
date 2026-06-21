from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings

class MembershipPlan(models.Model):
    """Membership Plans"""
    
    PLAN_TYPES = [
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('premium', 'Premium Plan'),
    ]
    
    DURATION_TYPES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    duration = models.CharField(max_length=20, choices=DURATION_TYPES, default='monthly')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Features as JSON
    features = models.JSONField(default=list, help_text="List of features")
    
    # Plan details
    description = models.TextField(blank=True)
    workout_plan_included = models.BooleanField(default=True)
    diet_plan_included = models.BooleanField(default=True)
    personal_trainer = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.duration} (₹{self.price})"
    
    def get_duration_days(self):
        """Get number of days for this plan"""
        if self.duration == 'monthly':
            return 30
        elif self.duration == 'quarterly':
            return 90
        elif self.duration == 'yearly':
            return 365
        return 0
    
    class Meta:
        ordering = ['price']
        verbose_name = 'Membership Plan'
        verbose_name_plural = 'Membership Plans'


class UserMembership(models.Model):
    """Track user membership purchases"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Payment info (will link to payment later)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if membership is currently active"""
        return self.status == 'active' and timezone.now() <= self.end_date
    
    def days_remaining(self):
        """Get days remaining in membership"""
        if self.is_active():
            remaining = (self.end_date - timezone.now()).days
            return max(0, remaining)
        return 0
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'User Membership'
        verbose_name_plural = 'User Memberships'