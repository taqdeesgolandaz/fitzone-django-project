from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta, datetime
from threading import Thread
from accounts.models import CustomUser
from membership.models import MembershipPlan, UserMembership
from payments.models import Payment
from workouts.models import WorkoutPlan, UserWorkoutProgress
from diet.models import UserDietProgress
from trainers.models import TrainerSession
from .models import AuditLog
from notifications.services import NotificationService
from notifications.email_templates import get_account_deleted_email
import json
from decimal import Decimal
from notifications.models import NewsletterSubscriber
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _is_test_or_debug_account(user):
    """Return True for obvious test/debug accounts that should not appear in admin reports."""
    if not user:
        return True

    username = (user.username or '').lower()
    email = (user.email or '').lower()

    if username.startswith(('debuguser', 'verifyuser', 'testuser', 'demo', 'sample')):
        return True
    if username.startswith('test') and username != 'test':
        return True
    if email.endswith('@example.com') or email.endswith('@example.org') or '@example.' in email:
        return True
    return False


def log_audit_action(admin_user, target_user, action, description='', request=None):
    """Log administrative action."""
    audit = AuditLog(
        admin_user=admin_user,
        target_user=target_user,
        action=action,
        description=description,
        ip_address=get_client_ip(request) if request else None
    )
    audit.save()
    return audit


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with analytics"""
    
    # Get date ranges
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    
    total_subscribers = NewsletterSubscriber.objects.count()

    # ==================== USER STATISTICS ====================
    user_stats = CustomUser.objects.filter(is_staff=False).aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        new_today=Count('id', filter=Q(date_joined__date=today)),
        new_this_month=Count('id', filter=Q(date_joined__date__gte=start_of_month))
    )
    total_users = user_stats['total']
    active_users = user_stats['active']
    new_users_today = user_stats['new_today']
    new_users_this_month = user_stats['new_this_month']
    
    # ==================== MEMBERSHIP STATISTICS ====================
    membership_stats = UserMembership.objects.aggregate(
        active=Count('id', filter=Q(status='active', end_date__gte=timezone.now())),
        total=Count('id')
    )
    active_memberships = membership_stats['active']
    total_memberships_sold = membership_stats['total']
    
    # Membership distribution with single query
    membership_distribution = list(MembershipPlan.objects.filter(is_active=True).annotate(
        count=Count('usermembership', filter=Q(usermembership__status='active'))
    ).values('name', 'count').order_by('-count'))
    
    for item in membership_distribution:
        name = item['name']
        item['color'] = '#E94560' if 'Pro' in name else '#00D09C' if 'Premium' in name else '#F5A623'
    
    # ==================== REVENUE STATISTICS ====================
    revenue_stats = Payment.objects.filter(status='success').aggregate(
        total=Sum('amount'),
        today=Sum('amount', filter=Q(paid_at__date=today)),
        month=Sum('amount', filter=Q(paid_at__date__gte=start_of_month)),
        year=Sum('amount', filter=Q(paid_at__date__gte=start_of_year))
    )
    total_revenue = revenue_stats['total'] or 0
    revenue_today = revenue_stats['today'] or 0
    revenue_this_month = revenue_stats['month'] or 0
    revenue_this_year = revenue_stats['year'] or 0
    
    # Calculate growth percentage
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    revenue_last_month = Payment.objects.filter(
        status='success', 
        paid_at__date__gte=last_month_start,
        paid_at__date__lt=start_of_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    revenue_growth = 0
    if revenue_last_month > 0:
        revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    
    # ==================== MONTHLY REVENUE CHART ====================
    monthly_revenue = []
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30 * (11 - i))
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        revenue = Payment.objects.filter(
            status='success',
            paid_at__date__gte=month_start,
            paid_at__date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_revenue.append({
            'month': month_date.strftime('%b'),
            'revenue': float(revenue)
        })
    
    # ==================== WORKOUT STATISTICS ====================
    workout_stats = UserWorkoutProgress.objects.filter(status='completed').aggregate(
        total=Count('id'),
        calories=Sum('calories_burned'),
        minutes=Sum('duration_minutes')
    )
    total_workouts_completed = workout_stats['total']
    total_calories_burned = workout_stats['calories'] or 0
    total_workout_minutes = workout_stats['minutes'] or 0
    
    # Most popular workout plans with single query
    popular_workouts = list(WorkoutPlan.objects.annotate(
        count=Count('userworkoutprogress')
    ).filter(count__gt=0).values('name', 'count').order_by('-count')[:5])
    
    # ==================== TRAINER STATISTICS ====================
    trainer_stats = TrainerSession.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        pending=Count('id', filter=Q(status='pending'))
    )
    total_sessions = trainer_stats['total']
    completed_sessions = trainer_stats['completed']
    pending_sessions = trainer_stats['pending']
    
    # ==================== RECENT ACTIVITIES ====================
    recent_payments = Payment.objects.filter(status='success').select_related('user').order_by('-created_at')[:10]
    recent_users = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    recent_memberships = UserMembership.objects.filter(status='active').select_related('plan', 'user').order_by('-start_date')[:10]
    
    # ==================== TODAY'S ACTIVITIES ====================
    today_payments = Payment.objects.filter(status='success', paid_at__date=today).count()
    today_workouts = UserWorkoutProgress.objects.filter(completed_date__date=today, status='completed').count()
    
    # ==================== RECENT DEACTIVATIONS & DELETIONS ====================
    recent_deactivations = AuditLog.objects.filter(action='deactivate').select_related('target_user', 'admin_user').order_by('-timestamp')[:8]
    recent_deletions = AuditLog.objects.filter(action='delete').select_related('admin_user').order_by('-timestamp')[:8]
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'new_users_this_month': new_users_this_month,
        'user_growth': round((new_users_this_month / max(total_users, 1)) * 100, 1),
        
        # Membership stats
        'active_memberships': active_memberships,
        'total_memberships_sold': total_memberships_sold,
        'membership_distribution': json.dumps(membership_distribution),
        
        # Revenue stats
        'total_revenue': float(total_revenue),
        'revenue_today': float(revenue_today),
        'revenue_this_month': float(revenue_this_month),
        'revenue_this_year': float(revenue_this_year),
        'revenue_growth': round(revenue_growth, 1),
        'monthly_revenue': json.dumps(monthly_revenue),
        
        # Workout stats
        'total_workouts_completed': total_workouts_completed,
        'total_calories_burned': round(total_calories_burned),
        'total_workout_minutes': round(total_workout_minutes),
        'popular_workouts': popular_workouts,
        
        # Trainer stats
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'pending_sessions': pending_sessions,
        'session_completion_rate': round((completed_sessions / max(total_sessions, 1)) * 100, 1),
        
        # Recent activities
        'recent_payments': recent_payments,
        'recent_users': recent_users,
        'recent_memberships': recent_memberships,
        'recent_deactivations': recent_deactivations,
        'recent_deletions': recent_deletions,
        
        # Today's activities
        'today_new_users': new_users_today,
        'today_payments': today_payments,
        'today_workouts': today_workouts,
        'total_subscribers': total_subscribers,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


@staff_member_required
def revenue_report(request):
    """Detailed revenue report"""
    payments = Payment.objects.filter(status='success').order_by('-created_at')
    
    # Group by payment method
    payment_methods = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    context = {
        'payments': payments[:100],
        'payment_methods': payment_methods,
        'total_revenue': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'admin_dashboard/revenue_report.html', context)


@staff_member_required
def user_report(request):
    """Detailed user report with search and filters"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    recently_registered_date = today - timedelta(days=7)  # Last 7 days

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    membership_filter = request.GET.get('membership', 'all')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')

    # Base queryset - exclude staff
    users = CustomUser.objects.filter(is_staff=False)

    # ==================== STATUS FILTER ====================
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = CustomUser.objects.filter(is_staff=True)

    # ==================== MEMBERSHIP FILTER ====================
    if membership_filter == 'with_membership':
        users = users.filter(membership_active=True)
    elif membership_filter == 'without_membership':
        users = users.filter(membership_active=False)
    elif membership_filter == 'recently_registered':
        users = users.filter(date_joined__date__gte=recently_registered_date)

    # ==================== DATE RANGE FILTER ====================
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            users = users.filter(date_joined__date__gte=date_from_parsed)
        except ValueError:
            date_from = ''

    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            users = users.filter(date_joined__date__lte=date_to_parsed)
        except ValueError:
            date_to = ''

    # ==================== SEARCH FILTER ====================
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mobile_number__icontains=search_query)
        )

    users = users.order_by('-date_joined')

    context = {
        'users': users,
        'total_users': CustomUser.objects.filter(is_staff=False).count(),
        'active_users': CustomUser.objects.filter(is_active=True, is_staff=False).count(),
        'status_filter': status_filter,
        'membership_filter': membership_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'filtered_users_count': users.count(),
        'last_month_start': last_month_start,
        'last_month_end': last_month_end,
    }
    return render(request, 'admin_dashboard/user_report.html', context)


@staff_member_required
def user_details_view(request, user_id):
    """View complete user profile, membership history, payments, and stats."""
    user = get_object_or_404(CustomUser, id=user_id)

    current_membership = UserMembership.objects.filter(
        user=user,
        status='active',
        end_date__gte=timezone.now()
    ).select_related('plan').first()

    membership_history = UserMembership.objects.filter(user=user).select_related('plan').order_by('-start_date')
    payments = Payment.objects.filter(user=user).order_by('-created_at')
    workout_sessions = UserWorkoutProgress.objects.filter(user=user).count()
    diet_plans_count = UserDietProgress.objects.filter(user=user).values('diet_plan').distinct().count()

    total_payments = payments.count()
    total_amount_spent = payments.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    active_memberships = membership_history.filter(status='active').count()
    cancelled_memberships = membership_history.filter(status='cancelled').count()

    days_remaining = 0
    if current_membership:
        days_remaining = max(0, (current_membership.end_date - timezone.now()).days)

    context = {
        'profile_user': user,
        'current_membership': current_membership,
        'membership_history': membership_history,
        'payments': payments,
        'total_payments': total_payments,
        'total_amount_spent': float(total_amount_spent),
        'active_memberships': active_memberships,
        'cancelled_memberships': cancelled_memberships,
        'workout_sessions': workout_sessions,
        'diet_plans_count': diet_plans_count,
        'days_remaining': days_remaining,
    }
    return render(request, 'admin_dashboard/user_details.html', context)


@staff_member_required
@require_http_methods(["POST"])
def cancel_membership(request, membership_id):
    """Cancel a specific membership and reset user subscription"""
    membership = get_object_or_404(UserMembership, id=membership_id)
    user = membership.user

    if membership.status == 'cancelled':
        messages.info(request, f'Membership for {user.username} is already cancelled.')
        return redirect('admin_dashboard:membership_report')

    with transaction.atomic():
        membership.status = 'cancelled'
        membership.save(update_fields=['status'])

        # Recompute the user's active membership state after cancellation.
        if user.has_active_membership():
            messages.success(request, f'Membership for {user.username} cancelled. Their current active membership remains intact.')
        else:
            user.membership_active = False
            user.current_membership = None
            user.membership_expiry = None
            user.save(update_fields=['membership_active', 'current_membership', 'membership_expiry'])
            messages.success(request, f'Membership for {user.username} cancelled. Notification sent to user.')

    # Send notification to user if the cancellation was effective
    try:
        NotificationService.create_notification(
            user=user,
            title='❌ Membership Cancelled',
            message=f'Your {membership.plan.name} membership has been cancelled. You can purchase a new plan at any time.',
            notification_type='membership',
            link='/membership/plans/'
        )
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

    return redirect('admin_dashboard:membership_report')


@staff_member_required
def membership_report(request):
    """Detailed membership report"""
    memberships = UserMembership.objects.select_related('user', 'plan').order_by('-start_date')
    latest_memberships = []
    seen_users = set()
    for membership in memberships:
        if membership.user_id in seen_users:
            continue
        if _is_test_or_debug_account(membership.user):
            continue
        seen_users.add(membership.user_id)
        latest_memberships.append(membership)

    active_memberships_count = sum(1 for membership in latest_memberships if membership.status == 'active')
    expired_memberships_count = sum(1 for membership in latest_memberships if membership.status == 'expired')
    
    context = {
        'memberships': latest_memberships,
        'total_memberships': len(latest_memberships),
        'active_memberships': active_memberships_count,
        'expired_memberships': expired_memberships_count,
    }
    return render(request, 'admin_dashboard/membership_report.html', context)


@staff_member_required
def trainer_report(request):
    """Detailed trainer sessions report"""
    sessions = TrainerSession.objects.select_related('trainer', 'user').order_by('-created_at')
    
    context = {
        'sessions': sessions,
        'total_sessions': sessions.count(),
        'completed_sessions': sessions.filter(status='completed').count(),
        'pending_sessions': sessions.filter(status='pending').count(),
        'cancelled_sessions': sessions.filter(status='cancelled').count(),
    }
    return render(request, 'admin_dashboard/trainer_report.html', context)


@staff_member_required
def workout_report(request):
    """Detailed workout progress report"""
    workouts = UserWorkoutProgress.objects.select_related('user', 'workout_plan').order_by('-completed_date')
    
    context = {
        'workouts': workouts,
        'total_workouts': workouts.count(),
        'completed_workouts': workouts.filter(status='completed').count(),
        'in_progress_workouts': workouts.filter(status='in_progress').count(),
        'total_calories_burned': workouts.filter(status='completed').aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0,
        'total_duration': workouts.filter(status='completed').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
    }
    return render(request, 'admin_dashboard/workout_report.html', context)


@staff_member_required
def member_details(request, user_id):
    """View complete user information and membership history"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Get current active membership
    current_membership = UserMembership.objects.filter(
        user=user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    # Get all memberships for this user (sorted by start date, newest first)
    membership_history = UserMembership.objects.filter(user=user).select_related('plan').order_by('-start_date')
    
    # Get all payments for this user
    payments = Payment.objects.filter(user=user).order_by('-created_at')
    
    # Calculate statistics
    total_memberships = membership_history.count()
    active_memberships = membership_history.filter(status='active').count()
    cancelled_memberships = membership_history.filter(status='cancelled').count()
    total_amount_spent = membership_history.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Calculate days remaining
    days_remaining = 0
    if current_membership:
        days_remaining = (current_membership.end_date - timezone.now()).days
    
    context = {
        'user': user,
        'current_membership': current_membership,
        'membership_history': membership_history,
        'payments': payments,
        'total_memberships': total_memberships,
        'active_memberships': active_memberships,
        'cancelled_memberships': cancelled_memberships,
        'total_amount_spent': float(total_amount_spent),
        'days_remaining': max(0, days_remaining),
    }
    
    return render(request, 'admin_dashboard/member_details.html', context)


# ==================== USER MANAGEMENT ACTIONS ====================

@staff_member_required
def deactivate_user_view(request, user_id):
    """Deactivate a user account (safe delete)"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent deactivating superusers/staff
    if user.is_staff or user.is_superuser:
        messages.error(request, 'Cannot deactivate staff or superuser accounts.')
        return redirect('admin_dashboard:user_details', user_id=user_id)
    
    if request.method == 'POST':
        if user.id == request.user.id:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('admin_dashboard:user_details', user_id=user_id)
        
        # Deactivate account
        user.is_active = False
        user.save()
        
        # Log the action
        log_audit_action(
            admin_user=request.user,
            target_user=user,
            action='deactivate',
            description=f'Account deactivated by {request.user.username}',
            request=request
        )
        
        # Send deactivation email
        try:
            NotificationService.send_account_deactivated_email(user, request.user)
            messages.success(request, f'User {user.username} has been deactivated. Notification email sent.')
        except Exception as e:
            messages.success(request, f'User {user.username} has been deactivated (email notification failed).')
        
        return redirect('admin_dashboard:user_report')
    
    context = {'profile_user': user}
    return render(request, 'admin_dashboard/user_details.html', context)


@staff_member_required
def delete_user_view(request, user_id):
    """Show delete confirmation for a user"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent deleting superusers/staff
    if user.is_staff or user.is_superuser:
        messages.error(request, 'Cannot delete staff or superuser accounts.')
        return redirect('admin_dashboard:user_details', user_id=user_id)
    
    # Get related data counts
    membership_count = UserMembership.objects.filter(user=user).count()
    payment_count = Payment.objects.filter(user=user).count()
    
    context = {
        'profile_user': user,
        'membership_count': membership_count,
        'payment_count': payment_count,
        'delete_mode': True,
    }
    return render(request, 'admin_dashboard/user_delete_confirm.html', context)


@staff_member_required
@require_http_methods(["POST"])
def confirm_delete_user_view(request, user_id):
    """Permanently delete a user account"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent deleting superusers/staff
    if user.is_staff or user.is_superuser:
        messages.error(request, 'Cannot delete staff or superuser accounts.')
        return redirect('admin_dashboard:user_details', user_id=user_id)
    
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_dashboard:user_details', user_id=user_id)
    
    username = user.username
    email = user.email
    full_name = user.full_name
    
    # Log the action BEFORE deletion
    log_audit_action(
        admin_user=request.user,
        target_user=user,
        action='delete',
        description=f'User account permanently deleted. Username: {username}, Email: {email}',
        request=request
    )
    
    # Delete the user immediately (don't wait for email)
    user.delete()
    
    # Send deletion email ASYNCHRONOUSLY after deletion
    def send_deletion_email_async():
        try:
            html_content, plain_content = get_account_deleted_email(user)
            send_mail(
                subject="Your FitZone Account Has Been Deleted",
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending deletion email: {e}")
    
    # Start email sending in background thread (non-blocking)
    thread = Thread(target=send_deletion_email_async, daemon=True)
    thread.start()
    
    messages.success(request, f'User {username} ({email}) has been permanently deleted.')
    return redirect('admin_dashboard:user_report')


@staff_member_required
@require_http_methods(["POST"])
def reactivate_user_view(request, user_id):
    """Reactivate a previously deactivated user"""
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_active:
        messages.info(request, 'User account is already active.')
        return redirect('admin_dashboard:user_details', user_id=user_id)

    user.is_active = True
    user.save()

    log_audit_action(
        admin_user=request.user,
        target_user=user,
        action='reactivate',
        description=f'Account reactivated by {request.user.username}',
        request=request
    )

    try:
        NotificationService.send_account_reactivated_email(user, request.user)
        messages.success(request, f'User {user.username} reactivated and notified.')
    except Exception:
        messages.success(request, f'User {user.username} reactivated (email failed).')

    return redirect('admin_dashboard:user_details', user_id=user_id)


@staff_member_required
def recreate_user_view(request, audit_id):
    """Show confirmation and recreate a deleted user from an AuditLog entry."""
    audit = get_object_or_404(AuditLog, id=audit_id)
    if audit.action != 'delete':
        messages.error(request, 'Audit entry is not a deletion.')
        return redirect('admin_dashboard:user_report')

    payload = None
    try:
        payload = json.loads(audit.description)
    except Exception:
        # Attempt to extract username/email from simple text
        import re
        m_user = re.search(r'Username:\s*([^,\n]+)', audit.description)
        m_email = re.search(r'Email:\s*([^,\n]+)', audit.description)
        if m_user or m_email:
            payload = {
                'username': m_user.group(1).strip() if m_user else None,
                'email': m_email.group(1).strip() if m_email else None,
            }

    if request.method == 'POST':
        if not payload or not payload.get('email'):
            messages.error(request, 'Cannot recover user: no usable email in audit data.')
            return redirect('admin_dashboard:user_report')

        if CustomUser.objects.filter(email=payload.get('email')).exists():
            messages.error(request, 'A user with that email already exists.')
            return redirect('admin_dashboard:user_report')

        with transaction.atomic():
            username = payload.get('username') or payload.get('email').split('@')[0]
            user = CustomUser.objects.create(
                username=username,
                email=payload.get('email'),
                is_active=True,
            )
            user.set_unusable_password()
            user.save()

        log_audit_action(
            admin_user=request.user,
            target_user=user,
            action='recreate',
            description=f'Recreated from audit {audit.id}',
            request=request
        )

        try:
            reset_url = f"{settings.SITE_URL}/forgot-password/" if hasattr(settings, 'SITE_URL') else '/forgot-password/'
            NotificationService.send_account_recovered_email(user, reset_url=reset_url, admin_user=request.user)
        except Exception:
            pass

        messages.success(request, f'User {user.username} recreated successfully and recovery email sent.')
        return redirect('admin_dashboard:user_details', user_id=user.id)

    if not payload or not payload.get('email'):
        messages.error(request, 'No usable data found in audit to recreate user.')
        return redirect('admin_dashboard:user_report')

    return render(request, 'admin_dashboard/user_recreate_confirm.html', {
        'audit': audit,
        'payload': payload or {},
    })


@staff_member_required
@require_http_methods(["POST"])
def edit_user_email(request, user_id):
    """Update user email address from admin panel"""
    user = get_object_or_404(CustomUser, id=user_id)
    new_email = request.POST.get('email', '').strip()
    
    # Validate email
    if not new_email:
        return JsonResponse({'success': False, 'error': 'Email cannot be empty'}, status=400)
    
    # Check if email already exists
    if CustomUser.objects.filter(email=new_email).exclude(id=user_id).exists():
        return JsonResponse({'success': False, 'error': 'Email already in use by another user'}, status=400)
    
    # Update email
    old_email = user.email
    user.email = new_email
    user.save(update_fields=['email'])
    
    # Log audit action
    log_audit_action(
        admin_user=request.user,
        target_user=user,
        action='update_email',
        description=f'Email changed from {old_email} to {new_email}',
        request=request
    )
    
    return JsonResponse({
        'success': True, 
        'message': f'Email updated from {old_email} to {new_email}',
        'new_email': new_email
    })
