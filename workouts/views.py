from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import WorkoutPlan, WorkoutCategory, UserWorkoutProgress, Exercise
from accounts.decorators import membership_required

# Day order for sorting
DAY_ORDER = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 7,
}

def _get_user_plan_type(user):
    if not user.is_authenticated:
        return None

    if getattr(user, 'has_active_membership', lambda: False)():
        current = getattr(user, 'current_membership', None)
        if not current:
            try:
                current = user.memberships.filter(status='active', end_date__gt=timezone.now()).first()
            except Exception:
                current = None
        if current:
            plan_type = getattr(current, 'plan_type', None)
            if not plan_type and hasattr(current, 'plan'):
                plan_type = getattr(current.plan, 'plan_type', None)
            return plan_type
    return None


@membership_required
def workout_list(request):
    """Display workout plans based on membership level"""

    user_plan = _get_user_plan_type(request.user)
    categories = WorkoutCategory.objects.filter(is_active=True)

    # Filter workouts based on membership level
    if user_plan == 'premium':
        beginner_workouts = WorkoutPlan.objects.filter(difficulty='beginner', is_active=True)
        intermediate_workouts = WorkoutPlan.objects.filter(difficulty='intermediate', is_active=True)
        advanced_workouts = WorkoutPlan.objects.filter(difficulty='advanced', is_active=True)
    elif user_plan == 'pro':
        beginner_workouts = WorkoutPlan.objects.filter(difficulty='beginner', is_active=True)[:10]
        intermediate_workouts = WorkoutPlan.objects.filter(difficulty='intermediate', is_active=True)[:10]
        advanced_workouts = WorkoutPlan.objects.filter(difficulty='advanced', is_active=True)[:5]
    else:  # Basic or anonymous
        beginner_workouts = WorkoutPlan.objects.filter(difficulty='beginner', is_active=True)[:5]
        intermediate_workouts = WorkoutPlan.objects.filter(difficulty='intermediate', is_active=True)[:3]
        advanced_workouts = WorkoutPlan.objects.filter(difficulty='advanced', is_active=True)[:2]

    # Sort by day order
    beginner_workouts = sorted(beginner_workouts, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))
    intermediate_workouts = sorted(intermediate_workouts, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))
    advanced_workouts = sorted(advanced_workouts, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))

    # Upgrade flow is transient per-request via ?upgrade=pro or ?upgrade=premium
    request_upgrade = request.GET.get('upgrade', '').lower()
    is_in_upgrade_flow = request_upgrade in {'pro', 'premium'}
    selected_upgrade_plan = request_upgrade
    is_target_selected = selected_upgrade_plan in {'pro', 'premium'}
    is_premium_selected = selected_upgrade_plan == 'premium'
    is_upgrade_page = False
    is_checkout_page = False

    # Decide which upgrade banners to show.
    pro_action_url = reverse('membership:plans') + '?upgrade=pro'
    premium_action_url = reverse('membership:plans') + '?upgrade=premium'

    show_pro_banner = False
    show_premium_banner = False
    # Basic users: show Pro banner only. Pro users: show Premium banner only.
    if user_plan == 'pro':
        show_premium_banner = not is_in_upgrade_flow
    elif user_plan == 'premium':
        show_pro_banner = False
        show_premium_banner = False
    else:
        # Treat unauthenticated or other values as Basic
        show_pro_banner = not is_in_upgrade_flow
        show_premium_banner = False

    pro_message = "Upgrade to Pro for more workout plans and features!"
    premium_message = "Upgrade to Premium for unlimited workout plans!"

    context = {
        'categories': categories,
        'beginner_workouts': beginner_workouts,
        'intermediate_workouts': intermediate_workouts,
        'advanced_workouts': advanced_workouts,
        'user_plan': user_plan,
        'selected_upgrade_plan': selected_upgrade_plan,
        'is_target_selected': is_target_selected,
        'membership_required': False,
        'is_upgrade_page': is_upgrade_page,
        'is_checkout_page': is_checkout_page,
        'is_premium_selected': is_premium_selected,
        'is_in_upgrade_flow': is_in_upgrade_flow,
        'show_pro_banner': show_pro_banner,
        'show_premium_banner': show_premium_banner,
        'pro_action_url': pro_action_url,
        'premium_action_url': premium_action_url,
        'pro_message': pro_message,
        'premium_message': premium_message,
    }
    return render(request, 'workouts/list.html', context)


@membership_required
def workout_detail(request, plan_id):
    """Display workout plan details"""
    workout_plan = get_object_or_404(WorkoutPlan, id=plan_id, is_active=True)
    
    # Get exercises for this plan
    workout_exercises = workout_plan.workoutplanexercise_set.all().select_related('exercise').order_by('order')
    
    # Check if user has completed this workout today
    user_progress = None
    today_workout = None
    if request.user.is_authenticated:
        today_workout = UserWorkoutProgress.objects.filter(
            user=request.user,
            workout_plan=workout_plan,
            scheduled_date=timezone.now().date()
        ).first()
        
        if not today_workout:
            # Create a new progress record for today
            today_workout = UserWorkoutProgress.objects.create(
                user=request.user,
                workout_plan=workout_plan,
                scheduled_date=timezone.now().date(),
                status='pending'
            )
    
    context = {
        'workout_plan': workout_plan,
        'exercises': workout_exercises,
        'today_workout': today_workout,
        'membership_required': False,
    }
    return render(request, 'workouts/detail.html', context)


@membership_required
def start_workout(request, plan_id):
    """Start tracking a workout"""
    # Membership decorator already enforces access; keep a fallback that shows the membership template
    try:
        has_active_membership = request.user.is_staff or getattr(request.user, 'has_active_membership', lambda: False)()
    except Exception:
        has_active_membership = False

    if not has_active_membership:
        return render(request, 'tracking/membership_required.html')
    
    workout_plan = get_object_or_404(WorkoutPlan, id=plan_id, is_active=True)
    
    # Check if already started today
    existing = UserWorkoutProgress.objects.filter(
        user=request.user,
        workout_plan=workout_plan,
        scheduled_date=timezone.now().date()
    ).first()
    
    if not existing:
        progress = UserWorkoutProgress.objects.create(
            user=request.user,
            workout_plan=workout_plan,
            scheduled_date=timezone.now().date(),
            status='pending'
        )
    else:
        progress = existing
    
    # Redirect to tracking page
    return redirect('workouts:track_workout', progress_id=progress.id)


@membership_required
def track_workout(request, progress_id):
    """Track and complete a workout"""
    progress = get_object_or_404(UserWorkoutProgress, id=progress_id, user=request.user)
    workout_plan = progress.workout_plan
    exercises = workout_plan.workoutplanexercise_set.all().select_related('exercise').order_by('order')
    
    if request.method == 'POST':
        # Update overall workout progress
        progress.status = 'completed'
        progress.completed_date = timezone.now()
        progress.duration_minutes = int(request.POST.get('duration_minutes', 0))
        progress.calories_burned = int(request.POST.get('calories_burned', 0))
        progress.notes = request.POST.get('notes', '')
        progress.save()
        
        messages.success(request, f'Great job! You completed {workout_plan.name}! 💪')
        return redirect('workouts:my_progress')
    
    # Calculate total calories for this workout
    total_calories = sum(we.exercise.calories_burn for we in exercises)
    total_duration = sum(we.exercise.duration_minutes for we in exercises)
    
    context = {
        'progress': progress,
        'workout_plan': workout_plan,
        'exercises': exercises,
        'total_calories': total_calories,
        'total_duration': total_duration,
    }
    return render(request, 'workouts/track.html', context)

@membership_required
def my_progress(request):
    """Show user's workout progress"""
    from django.utils import timezone
    from .models import UserWorkoutProgress
    
    all_progress = UserWorkoutProgress.objects.filter(user=request.user)
    progress_records = all_progress.order_by('-scheduled_date')[:30]
    
    total = all_progress.count()
    completed = all_progress.filter(status='completed').count()
    total_calories = sum(p.calories_burned for p in all_progress if p.calories_burned)
    completion_rate = int((completed / total * 100)) if total > 0 else 0
    
    streak = 0
    completed_dates = set(all_progress.filter(status='completed').values_list('scheduled_date', flat=True))
    current_date = timezone.now().date()
    while current_date in completed_dates:
        streak += 1
        current_date -= timezone.timedelta(days=1)
    
    stats = {
        'total_workouts': total,
        'completed_workouts': completed,
        'completion_rate': completion_rate,
        'total_calories': total_calories,
        'streak': streak,
    }
    
    context = {
        'progress_records': progress_records,
        'stats': stats,
        'membership_required': False,
    }
    return render(request, 'workouts/progress.html', context)


def calculate_streak(progress_records):
    """Calculate current workout streak"""
    streak = 0
    completed_dates = set(progress_records.filter(status='completed').values_list('scheduled_date', flat=True))
    
    current_date = timezone.now().date()
    while current_date in completed_dates:
        streak += 1
        current_date -= timezone.timedelta(days=1)
    
    return streak