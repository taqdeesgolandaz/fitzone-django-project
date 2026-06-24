from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AuditLog(models.Model):
    """Log administrative actions on user accounts."""
    
    ACTION_CHOICES = [
        ('delete', 'Delete User'),
        ('deactivate', 'Deactivate User'),
        ('activate', 'Activate User'),
        ('edit', 'Edit User'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs_created')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs_target')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['admin_user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.admin_user} - {self.action} - {self.target_user} ({self.timestamp})"
