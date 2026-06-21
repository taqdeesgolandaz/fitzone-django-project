from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WorkoutPlan, WorkoutCategory, UserWorkoutProgress, Exercise

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

def workout_list(request):
    """Display all workout plans - Shows message if no membership"""
    
    # Check if user is not logged in
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user has active membership (admin/staff users are exempt)
    if not request.user.is_staff and not request.user.membership_active:
        return render(request, 'workouts/list.html', {
            'membership_required': True,
            'message': 'You need an active membership to access workout plans. Choose a plan that best suits your fitness goals!',
            'beginner_workouts': [],  # Add empty list
            'intermediate_workouts': [],  # Add empty list
            'advanced_workouts': [],  # Add empty list
        })
    
    # Rest of your code...
    categories = WorkoutCategory.objects.filter(is_active=True)
    
    beginner_workouts = list(WorkoutPlan.objects.filter(difficulty='beginner', is_active=True))
    intermediate_workouts = list(WorkoutPlan.objects.filter(difficulty='intermediate', is_active=True))
    advanced_workouts = list(WorkoutPlan.objects.filter(difficulty='advanced', is_active=True))
    
    beginner_workouts.sort(key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    intermediate_workouts.sort(key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    advanced_workouts.sort(key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    
    context = {
        'categories': categories,
        'beginner_workouts': beginner_workouts,
        'intermediate_workouts': intermediate_workouts,
        'advanced_workouts': advanced_workouts,
        'membership_required': False,
    }
    return render(request, 'workouts/list.html', context)


def workout_detail(request, plan_id):
    """Display workout plan details - Shows message if no membership"""
    
    # Check if user is not logged in
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user has active membership (admin/staff users are exempt)
    if not request.user.is_staff and not request.user.membership_active:
        return render(request, 'workouts/detail.html', {
            'membership_required': True,
            'message': 'You need an active membership to view workout details. Choose a plan that best suits your fitness goals!',
            'workout_plan': None,  # Add this
            'exercises': [],  # Add this - empty list to avoid template error
            'today_workout': None,  # Add this
        })
    
    # If has membership, show normal content
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


@login_required
def start_workout(request, plan_id):
    """Start tracking a workout"""
    # Check if user has active membership (admin/staff users are exempt)
    if not request.user.is_staff and not request.user.membership_active:
        messages.warning(request, 'You need an active membership to start a workout.')
        return redirect('membership:plans')
    
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


@login_required
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

def my_progress(request):
    """Show user's workout progress - Shows message if no membership"""
    
    # Check if user is not logged in
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user has active membership (admin/staff users are exempt)
    if not request.user.is_staff and not request.user.membership_active:
        return render(request, 'workouts/progress.html', {
            'membership_required': True,
            'message': 'You need an active membership to view your workout progress. Choose a plan that best suits your fitness goals!',
            'progress_records': [],
            'stats': {
                'total_workouts': 0,
                'completed_workouts': 0,
                'completion_rate': 0,
                'total_calories': 0,
                'streak': 0,
            },
        })
    
    # If has membership, show normal progress
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