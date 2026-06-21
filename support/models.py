from django.db import models
from django.conf import settings
from django.utils import timezone

class SupportMessage(models.Model):
    """Store support messages from users"""
    
    MESSAGE_TYPES = [
        ('contact', 'Contact Us'),
        ('support', 'Contact Support'),
        ('report', 'Report Problem'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]
    
    # User info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_messages')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Message details
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='contact')
    category = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=500)
    message = models.TextField()
    
    # For report problem
    problem_type = models.CharField(max_length=50, blank=True)
    steps_to_reproduce = models.TextField(blank=True)
    urgency = models.CharField(max_length=20, blank=True)
    device_info = models.CharField(max_length=500, blank=True)
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject} - {self.created_at}"
    
    def mark_as_read(self):
        if self.status == 'pending':
            self.status = 'read'
            self.save()
    
    def mark_as_replied(self):
        self.status = 'replied'
        self.save()
    
    def mark_as_resolved(self):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Message'
        verbose_name_plural = 'Support Messages'