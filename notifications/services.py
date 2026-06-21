from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from requests import session
from .models import Notification, EmailLog
from .email_templates import *

class NotificationService:
    """Service for sending notifications and emails"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type='system', link=''):
        """Create in-app notification"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
        return notification

    @staticmethod
    def create_staff_notification(title, message, notification_type='system', link=''):
        """Create the same notification for all staff users"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_users = User.objects.filter(is_staff=True)
        created = []
        for u in staff_users:
            n = Notification.objects.create(
                user=u,
                title=title,
                message=message,
                notification_type=notification_type,
                link=link
            )
            created.append(n)
        return created
    
    @staticmethod
    def send_email(user, subject, html_content, plain_content, email_type):
        """Send email and log it"""
        try:
            recipient_list = [user.email] if user else [subject]
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                recipient_list=recipient_list,
                html_message=html_content,
                fail_silently=False,
            )
            # Log success
            EmailLog.objects.create(
                user=user,
                email=user.email if user else subject,
                subject=subject,
                email_type=email_type,
                status='sent'
            )
            return True
        except Exception as e:
            # Log failure
            EmailLog.objects.create(
                user=user,
                email=user.email if user else subject,
                subject=subject,
                email_type=email_type,
                status='failed',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        subject = f"Welcome to FitZone, {user.full_name or user.username}! 🎉"
        html_content, plain_content = get_welcome_email(user)
        NotificationService.send_email(user, subject, html_content, plain_content, 'welcome')
        
        # Create in-app notification
        NotificationService.create_notification(
            user=user,
            title="Welcome to FitZone!",
            message=f"Welcome {user.full_name or user.username}! Start your fitness journey with us.",
            notification_type='system',
            link='/dashboard/'
        )


    @staticmethod
    def send_booking_confirmation_email(user, session):
        """Send booking confirmation email"""
        subject = f"Session Confirmed with {session.trainer.full_name}"
        html_content, plain_content = get_booking_confirmation_email(user, session)
        NotificationService.send_email(user, subject, html_content, plain_content, 'booking_confirmation')   
    
    @staticmethod
    def send_payment_success_email(user, payment, plan):
        """Send payment success email"""
        subject = f"Payment Successful - {plan.name} Membership"
        html_content, plain_content = get_payment_success_email(user, payment, plan)
        NotificationService.send_email(user, subject, html_content, plain_content, 'payment_success')
        
        # Create in-app notification
        NotificationService.create_notification(
            user=user,
            title="Payment Successful! 💰",
            message=f"Your payment of ₹{payment.amount} for {plan.name} was successful.",
            notification_type='payment',
            link='/payments/history/'
        )
    
    @staticmethod
    def send_membership_expiry_reminder(user, membership):
        """Send membership expiry reminder"""
        days_left = membership.days_remaining()
        subject = f"Membership Expiring Soon - {days_left} days left!"
        html_content, plain_content = get_membership_expiry_email(user, membership)
        NotificationService.send_email(user, subject, html_content, plain_content, 'membership_expiry')
        
        # Create in-app notification
        NotificationService.create_notification(
            user=user,
            title="Membership Expiring Soon! ⏰",
            message=f"Your {membership.plan.name} membership expires in {days_left} days. Renew now!",
            notification_type='membership',
            link='/membership/plans/'
        )
    
    @staticmethod
    def send_booking_confirmation_email(user, session):
        """Send booking confirmation email"""
        subject = f"Session Confirmed with {session.trainer.full_name}"
        html_content, plain_content = get_booking_confirmation_email(user, session)
        NotificationService.send_email(user, subject, html_content, plain_content, 'booking_confirmation')
        
        # Create in-app notification
        NotificationService.create_notification(
            user=user,
            title="Session Confirmed! ✅",
            message=f"Your session with {session.trainer.full_name} on {session.session_date} has been confirmed.",
            notification_type='trainer',
            link='/trainers/my-sessions/'
        )
