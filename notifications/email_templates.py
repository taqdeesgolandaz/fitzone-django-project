from django.template.loader import render_to_string
from django.utils.html import strip_tags

def get_welcome_email(user):
    """Welcome email template"""
    context = {
        'username': user.full_name or user.username,
        'email': user.email,
        'login_url': '/login/',
        'dashboard_url': '/dashboard/',
        'year': 2024,
    }
    html_content = render_to_string('notifications/emails/welcome.html', context)
    plain_content = strip_tags(html_content)
    return html_content, plain_content


def get_payment_success_email(user, payment, plan):
    """Payment success email template"""
    context = {
        'username': user.full_name or user.username,
        'amount': payment.amount,
        'plan_name': plan.name,
        'invoice_number': payment.invoice_number,
        'payment_date': payment.paid_at,
        'transaction_id': payment.razorpay_payment_id,
        'dashboard_url': '/dashboard/',
        'membership_url': '/membership/my-membership/',
        'year': 2024,
    }
    html_content = render_to_string('notifications/emails/payment_success.html', context)
    plain_content = strip_tags(html_content)
    return html_content, plain_content


def get_membership_expiry_email(user, membership):
    """Membership expiry reminder email"""
    days_left = membership.days_remaining()
    context = {
        'username': user.full_name or user.username,
        'plan_name': membership.plan.name,
        'days_left': days_left,
        'expiry_date': membership.end_date,
        'renewal_url': '/membership/plans/',
        'year': 2024,
    }
    html_content = render_to_string('notifications/emails/membership_expiry.html', context)
    plain_content = strip_tags(html_content)
    return html_content, plain_content


def get_booking_confirmation_email(user, session):
    """Booking confirmation email"""
    context = {
        'username': user.full_name or user.username,
        'trainer_name': session.trainer.full_name,
        'session_date': session.session_date,
        'session_time': session.session_time,
        'session_type': session.get_session_type_display(),
        'meeting_link': session.meeting_link or 'Will be shared soon',
        'my_sessions_url': '/trainers/my-sessions/',
        'year': 2024,
    }
    html_content = render_to_string('notifications/emails/booking_confirmation.html', context)
    plain_content = strip_tags(html_content)
    return html_content, plain_content


def get_workout_reminder_email(user, workout_plan):
    """Workout reminder email"""
    context = {
        'username': user.full_name or user.username,
        'workout_name': workout_plan.name,
        'day': workout_plan.get_day_of_week_display(),
        'workout_url': f'/workouts/plan/{workout_plan.id}/',
        'year': 2024,
    }
    html_content = render_to_string('notifications/emails/workout_reminder.html', context)
    plain_content = strip_tags(html_content)
    return html_content, plain_content


def get_account_deactivated_email(user):
    """Account deactivation notification email"""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', None) or 'http://localhost:8000'
    site = site_url.rstrip('/')
    reactivation_path = '/contact-support/'
    context = {
        'username': user.full_name or user.username,
        'reactivation_url': f"{site}{reactivation_path}",
        'year': 2026,
    }
    html_content = render_to_string('emails/account_deactivated.html', context)
    plain_content = f"""Hello {context['username']},

Your FitZone account has been deactivated. You cannot sign in while the account is deactivated.

If you want to reactivate your account, please contact support at support@fitzone.com and we will assist you.

Regards,
FitZone Team
"""
    return html_content, plain_content

def get_account_recovered_email(user, reset_url='/forgot-password/'):
    """Account recovered after deletion - instruct user to reset password"""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', None) or 'http://localhost:8000'
    site = site_url.rstrip('/')
    # allow caller to pass an absolute or relative reset_url
    if reset_url.startswith('http://') or reset_url.startswith('https://'):
        absolute_reset = reset_url
    else:
        absolute_reset = f"{site}{reset_url}"
    context = {
        'username': user.full_name or user.username,
        'reset_url': absolute_reset,
        'support_url': f"{site}/support/",
        'year': 2026,
    }
    html_content = render_to_string('emails/account_recovered.html', context)
    plain_content = f"""Hello {context['username']},

Your FitZone account has been recovered. Please reset your password to secure your account:
{context['reset_url']}

If you did not request this, contact support@fitzone.com

Regards,
FitZone Team
"""
    return html_content, plain_content

def get_account_deleted_email(user):
    """Account deletion notification email"""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', None) or 'http://localhost:8000'
    site = site_url.rstrip('/')
    support_path = '/contact-support/'
    context = {
        'username': user.full_name or user.username,
        'support_url': f"{site}{support_path}",
        'year': 2026,
    }
    # Render with matching username variable
    html_content = render_to_string('accounts/emails/account_deleted_by_admin.html', context)

    plain_content = f"""Hello {user.full_name or user.username},

Your FitZone account ({user.username}) has been deleted by an administrator and is no longer active.

If you believe this was a mistake, contact support: {context['support_url']}

Regards,
FitZone Team
"""
    return html_content, plain_content


def get_account_reactivated_email(user):
    """Account reactivated notification email"""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', None) or 'http://localhost:8000'
    site = site_url.rstrip('/')
    dashboard_path = '/dashboard/'
    context = {
        'username': user.full_name or user.username,
        'dashboard_url': f"{site}{dashboard_path}",
        'support_url': f"{site}/support/",
        'year': 2026,
    }
    html_content = render_to_string('emails/account_reactivated.html', context)
    plain_content = f"""Hello {context['username']},

Your FitZone account has been reactivated. You can sign in and access your dashboard: {context['dashboard_url']}

If you need help, contact support@fitzone.com

Regards,
FitZone Team
"""
    return html_content, plain_content

def get_password_reset_email(user, reset_link):
    """Password reset email"""
    username = user.full_name or user.username
    from django.utils import timezone
    # Use a portable strftime format and strip leading zero for hour (works on Windows)
    now = timezone.now()
    try:
        now_str = now.strftime('%I:%M %p').lstrip('0')
    except Exception:
        now_str = ''
    context = {
        'username': username,
        'reset_link': reset_link,
        'year': timezone.now().year,
        'now': now_str,
    }
    html_content = render_to_string('notifications/emails/password_reset.html', context)
    plain_content = f"""Hello {username},

We received a request to reset your FitZone password.

Please open this email and click the 'Reset Password' button to proceed. This link expires in 24 hours.

If you did not request this, ignore this message.

FitZone Team
"""
    return html_content, plain_content