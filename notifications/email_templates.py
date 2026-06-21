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