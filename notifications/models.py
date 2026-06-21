from django.db import models
from django.conf import settings
from django.utils import timezone

class NewsletterSubscriber(models.Model):
    """Store newsletter subscribers"""
    
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

class Notification(models.Model):
    """In-app notifications for users"""
    
    NOTIFICATION_TYPES = [
        ('membership', 'Membership'),
        ('payment', 'Payment'),
        ('workout', 'Workout'),
        ('diet', 'Diet'),
        ('trainer', 'Trainer'),
        ('achievement', 'Achievement'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    
    # Link to related object
    link = models.CharField(max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)  # For email tracking
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    class Meta:
        ordering = ['-created_at']


class EmailLog(models.Model):
    """Log of sent emails"""
    
    EMAIL_TYPES = [
        ('welcome', 'Welcome Email'),
        ('payment_success', 'Payment Success'),
        ('membership_expiry', 'Membership Expiry'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('workout_reminder', 'Workout Reminder'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='emails')
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    status = models.CharField(max_length=20, default='sent')  # sent, failed
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.email} - {self.subject} - {self.sent_at}"
    
    class Meta:
        ordering = ['-sent_at']