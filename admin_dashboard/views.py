from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, datetime
from accounts.models import CustomUser
from membership.models import MembershipPlan, UserMembership
from payments.models import Payment
from workouts.models import WorkoutPlan, UserWorkoutProgress
from trainers.models import TrainerSession
import json
from decimal import Decimal
from notifications.models import NewsletterSubscriber


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
    total_users = CustomUser.objects.filter(is_staff=False).count()
    active_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()
    new_users_today = CustomUser.objects.filter(date_joined__date=today, is_staff=False).count()
    new_users_this_month = CustomUser.objects.filter(date_joined__date__gte=start_of_month, is_staff=False).count()
    
    # ==================== MEMBERSHIP STATISTICS ====================
    active_memberships = UserMembership.objects.filter(
        status='active', 
        end_date__gte=timezone.now()
    ).count()
    
    total_memberships_sold = UserMembership.objects.count()
    
    # Membership distribution
    membership_distribution = []
    for plan in MembershipPlan.objects.all():
        count = UserMembership.objects.filter(plan=plan, status='active').count()
        membership_distribution.append({
            'name': plan.name,
            'count': count,
            'color': '#E94560' if plan.name == 'Pro Plan' else '#00D09C' if plan.name == 'Premium Plan' else '#F5A623'
        })
    
    # ==================== REVENUE STATISTICS ====================
    total_revenue = Payment.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_today = Payment.objects.filter(status='success', paid_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_this_month = Payment.objects.filter(status='success', paid_at__date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_this_year = Payment.objects.filter(status='success', paid_at__date__gte=start_of_year).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate growth percentage (compare with previous month)
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
    total_workouts_completed = UserWorkoutProgress.objects.filter(status='completed').count()
    total_calories_burned = UserWorkoutProgress.objects.filter(status='completed').aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    total_workout_minutes = UserWorkoutProgress.objects.filter(status='completed').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    
    # Most popular workout plans
    popular_workouts = []
    for plan in WorkoutPlan.objects.all():
        count = UserWorkoutProgress.objects.filter(workout_plan=plan).count()
        if count > 0:
            popular_workouts.append({
                'name': plan.name,
                'count': count
            })
    popular_workouts = sorted(popular_workouts, key=lambda x: x['count'], reverse=True)[:5]
    
    # ==================== TRAINER STATISTICS ====================
    total_sessions = TrainerSession.objects.count()
    completed_sessions = TrainerSession.objects.filter(status='completed').count()
    pending_sessions = TrainerSession.objects.filter(status='pending').count()
    
    # ==================== RECENT ACTIVITIES ====================
    recent_payments = Payment.objects.filter(status='success').order_by('-created_at')[:10]
    recent_users = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    recent_memberships = UserMembership.objects.filter(status='active').order_by('-start_date')[:10]
    
    # ==================== TODAY'S ACTIVITIES ====================
    today_new_users = CustomUser.objects.filter(date_joined__date=today, is_staff=False).count()
    today_payments = Payment.objects.filter(status='success', paid_at__date=today).count()
    today_workouts = UserWorkoutProgress.objects.filter(completed_date__date=today, status='completed').count()
    
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
        
        # Today's activities
        'today_new_users': today_new_users,
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
    """Detailed user report"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    status_filter = request.GET.get('status', 'all')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    users = CustomUser.objects.filter(is_staff=False)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

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

    users = users.order_by('-date_joined')

    context = {
        'users': users,
        'total_users': CustomUser.objects.filter(is_staff=False).count(),
        'active_users': CustomUser.objects.filter(is_active=True, is_staff=False).count(),
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'filtered_users_count': users.count(),
        'last_month_start': last_month_start,
        'last_month_end': last_month_end,
    }
    return render(request, 'admin_dashboard/user_report.html', context)


@staff_member_required
def cancel_membership(request, membership_id):
    """Cancel a specific membership and reset user subscription"""
    membership = get_object_or_404(UserMembership, id=membership_id)
    membership.status = 'cancelled'
    membership.save()
    
    # Reset user's membership flags
    user = membership.user
    user.membership_active = False
    user.current_membership = None
    user.membership_expiry = None
    user.save()
    
    # Send notification to user
    try:
        from notifications.services import NotificationService
        NotificationService.create_notification(
            user=user,
            title='❌ Membership Cancelled',
            message=f'Your {membership.plan.name} membership has been cancelled. You can purchase a new plan at any time.',
            notification_type='membership',
            link='/membership/plans/'
        )
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
    
    messages.success(request, f'Membership for {user.username} cancelled. Notification sent to user.')
    return redirect('admin_dashboard:membership_report')


@staff_member_required
def membership_report(request):
    """Detailed membership report"""
    memberships = UserMembership.objects.select_related('user', 'plan').order_by('-start_date')
    
    context = {
        'memberships': memberships,
        'total_memberships': memberships.count(),
        'active_memberships': memberships.filter(status='active').count(),
        'expired_memberships': memberships.filter(status='expired').count(),
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