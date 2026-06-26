from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import sys
import traceback
from .models import Notification, EmailLog
from .email_templates import *


def send_email_via_brevo(subject, plain_content, html_content, from_email, recipient_list):
    """Send email through Brevo Transactional Emails API when configured."""
    if not getattr(settings, 'BREVO_API_KEY', ''):
        return None

    try:
        import brevo_python
    except ImportError:
        print('Brevo API package not installed; falling back to SMTP.', file=sys.stderr)
        return None

    try:
        configuration = brevo_python.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_client = brevo_python.ApiClient(configuration)
        api_instance = brevo_python.TransactionalEmailsApi(api_client)

        sender_email = settings.BREVO_SENDER_EMAIL or from_email
        if '<' in sender_email and '>' in sender_email:
            sender_name = sender_email.split('<')[0].strip()
            sender_address = sender_email.split('<')[1].split('>')[0].strip()
            sender = {'email': sender_address, 'name': sender_name}
        else:
            sender = {'email': sender_email}

        send_smtp_email = brevo_python.SendSmtpEmail(
            to=[{'email': recipient} for recipient in recipient_list],
            sender=sender,
            subject=subject,
            html_content=html_content or plain_content,
            text_content=plain_content,
        )

        api_instance.send_transac_email(send_smtp_email)
        return True
    except Exception as e:
        print(f'Brevo API send failed: {e}', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False


class NotificationService:
    """Service for sending notifications and emails"""

    @staticmethod
    def create_notification(user, title, message, notification_type='system', link=''):
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
        """Send email and log it."""
        recipient_list = [user.email] if user else []
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None

        try:
            if settings.BREVO_API_KEY:
                brevo_result = send_email_via_brevo(
                    subject=subject,
                    plain_content=plain_content,
                    html_content=html_content,
                    from_email=settings.BREVO_SENDER_EMAIL or from_email,
                    recipient_list=recipient_list,
                )
                if brevo_result is True:
                    EmailLog.objects.create(
                        user=user,
                        email=user.email if user else None,
                        subject=subject,
                        email_type=email_type,
                        status='sent'
                    )
                    return True
                if brevo_result is False:
                    EmailLog.objects.create(
                        user=user,
                        email=user.email if user else None,
                        subject=subject,
                        email_type=email_type,
                        status='failed',
                        error_message='Brevo API send failed',
                    )
                    return False

            send_mail(
                subject=subject,
                message=plain_content,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_content,
                fail_silently=False,
            )
            EmailLog.objects.create(
                user=user,
                email=user.email if user else None,
                subject=subject,
                email_type=email_type,
                status='sent'
            )
            return True
        except Exception as e:
            EmailLog.objects.create(
                user=user,
                email=user.email if user else None,
                subject=subject,
                email_type=email_type,
                status='failed',
                error_message=str(e)
            )
            return False

    @staticmethod
    def send_welcome_email(user):
        subject = f"Welcome to FitZone, {user.full_name or user.username}! 🎉"
        html_content, plain_content = get_welcome_email(user)
        NotificationService.send_email(user, subject, html_content, plain_content, 'welcome')
        NotificationService.create_notification(
            user=user,
            title="Welcome to FitZone!",
            message=f"Welcome {user.full_name or user.username}! Start your fitness journey with us.",
            notification_type='system',
            link='/dashboard/'
        )

    @staticmethod
    def send_booking_confirmation_email(user, session):
        subject = f"Session Confirmed with {session.trainer.full_name}"
        html_content, plain_content = get_booking_confirmation_email(user, session)
        NotificationService.send_email(user, subject, html_content, plain_content, 'booking_confirmation')

    @staticmethod
    def send_payment_success_email(user, payment, plan):
        subject = f"Payment Successful - {plan.name} Membership"
        html_content, plain_content = get_payment_success_email(user, payment, plan)
        NotificationService.send_email(user, subject, html_content, plain_content, 'payment_success')
        NotificationService.create_notification(
            user=user,
            title="Payment Successful! 💰",
            message=f"Your payment of {payment.amount} for {plan.name} was successful.",
            notification_type='payment',
            link='/payments/history/'
        )

    @staticmethod
    def send_membership_expiry_reminder(user, membership):
        days_left = membership.days_remaining()
        subject = f"Membership Expiring Soon - {days_left} days left!"
        html_content, plain_content = get_membership_expiry_email(user, membership)
        NotificationService.send_email(user, subject, html_content, plain_content, 'membership_expiry')
        NotificationService.create_notification(
            user=user,
            title="Membership Expiring Soon! ⏰",
            message=f"Your {membership.plan.name} membership expires in {days_left} days. Renew now!",
            notification_type='membership',
            link='/membership/plans/'
        )

    @staticmethod
    def send_account_deactivated_email(user, admin_user=None):
        subject = f"Your FitZone Account Has Been Deactivated"
        html_content, plain_content = get_account_deactivated_email(user)
        NotificationService.send_email(user, subject, html_content, plain_content, 'account_deactivated')
        if admin_user:
            NotificationService.create_notification(
                user=admin_user,
                title=f"Account Deactivated: {user.username}",
                message=f"You have deactivated the account for {user.full_name or user.username}",
                notification_type='system',
                link=f'/admin/users/'
            )

    @staticmethod
    def send_account_reactivated_email(user, admin_user=None):
        subject = f"Your FitZone Account Has Been Reactivated"
        html_content, plain_content = get_account_reactivated_email(user)
        NotificationService.send_email(user, subject, html_content, plain_content, 'account_reactivated')
        if admin_user:
            NotificationService.create_notification(
                user=admin_user,
                title=f"Account Reactivated: {user.username}",
                message=f"You have reactivated the account for {user.full_name or user.username}",
                notification_type='system',
                link=f'/admin/users/'
            )

    @staticmethod
    def send_account_deleted_email(user_email, user_name, admin_user=None):
        subject = f"Your FitZone Account Has Been Deleted"
        class TempUser:
            def __init__(self, email, name):
                self.email = email
                self.full_name = name
                self.username = name
        temp_user = TempUser(user_email, user_name)
        html_content, plain_content = get_account_deleted_email(temp_user)
        try:
            NotificationService.send_email(temp_user, subject, html_content, plain_content, 'account_deleted')
            return True
        except Exception:
            return False

    @staticmethod
    def send_account_recovered_email(user, reset_url=None, admin_user=None):
        subject = f"Your FitZone Account Has Been Recovered"
        reset_link = reset_url or f"{settings.SITE_URL}/forgot-password/"
        html_content, plain_content = get_account_recovered_email(user, reset_link)
        NotificationService.send_email(user, subject, html_content, plain_content, 'account_recovered')
        if admin_user:
            NotificationService.create_notification(
                user=admin_user,
                title=f"Account Recovered: {user.username}",
                message=f"You have recovered the account for {user.full_name or user.username}",
                notification_type='system',
                link=f'/admin/users/'
            )
