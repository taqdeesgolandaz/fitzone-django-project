from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Min, Max
from .models import FitnessProgress, UserFitnessGoal, WorkoutLog
from datetime import timedelta
import json
from django.utils import timezone as dj_timezone
from membership.models import UserMembership

@login_required
def tracking_dashboard(request):
    """Main tracking dashboard with charts"""
    # Get user's progress records (last 30 days)
    progress_records = FitnessProgress.objects.filter(
        user=request.user
    ).order_by('-date_recorded')[:30]
    
    # Prepare chart data
    chart_data = {
        'dates': [],
        'weights': [],
        'bmis': [],
        'body_fats': [],
    }
    
    for record in reversed(progress_records):  # Reverse for chronological order
        chart_data['dates'].append(record.date_recorded.strftime('%b %d'))
        chart_data['weights'].append(record.weight)
        if record.bmi:
            chart_data['bmis'].append(record.bmi)
        if record.body_fat_percentage:
            chart_data['body_fats'].append(record.body_fat_percentage)
    
    # Get latest progress
    latest_progress = progress_records.first()
    
    # Get user's goal
    goal = UserFitnessGoal.objects.filter(user=request.user, is_active=True).first()
    
    # Calculate stats
    stats = calculate_stats(request.user, progress_records)
    
    context = {
        'progress_records': progress_records[:10],
        'latest_progress': latest_progress,
        'goal': goal,
        'stats': stats,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'tracking/dashboard.html', context)


@login_required
def add_progress(request):
    """Add new fitness progress entry"""
    if request.method == 'POST':
        weight = request.POST.get('weight')
        height = request.POST.get('height', request.user.height)
        body_fat = request.POST.get('body_fat_percentage')
        chest = request.POST.get('chest')
        waist = request.POST.get('waist')
        hips = request.POST.get('hips')
        notes = request.POST.get('notes')
        
        # Check if entry already exists for today
        existing = FitnessProgress.objects.filter(
            user=request.user,
            date_recorded=timezone.now().date()
        ).first()
        
        if existing:
            messages.warning(request, 'You already logged progress today. Edit the existing entry instead.')
            return redirect('tracking:dashboard')
        
        progress = FitnessProgress.objects.create(
            user=request.user,
            weight=weight,
            height=height or request.user.height,
            body_fat_percentage=body_fat,
            chest=chest,
            waist=waist,
            hips=hips,
            notes=notes
        )
        
        # Update user's current weight and height
        request.user.weight = weight
        if height:
            request.user.height = height
        request.user.save()
        
        messages.success(request, 'Progress recorded successfully!')
        return redirect('tracking:dashboard')
    
    return render(request, 'tracking/add_progress.html')


@login_required
def edit_progress(request, progress_id):
    """Edit existing progress entry"""
    progress = get_object_or_404(FitnessProgress, id=progress_id, user=request.user)
    
    if request.method == 'POST':
        progress.weight = request.POST.get('weight')
        progress.body_fat_percentage = request.POST.get('body_fat_percentage')
        progress.chest = request.POST.get('chest')
        progress.waist = request.POST.get('waist')
        progress.hips = request.POST.get('hips')
        progress.notes = request.POST.get('notes')
        progress.save()
        
        messages.success(request, 'Progress updated successfully!')
        return redirect('tracking:dashboard')
    
    return render(request, 'tracking/edit_progress.html', {'progress': progress})


@login_required
def delete_progress(request, progress_id):
    """Delete progress entry"""
    progress = get_object_or_404(FitnessProgress, id=progress_id, user=request.user)
    progress.delete()
    messages.success(request, 'Progress entry deleted.')
    return redirect('tracking:dashboard')


@login_required
def set_goal(request):
    """Set or update fitness goal"""
    goal, created = UserFitnessGoal.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        goal.goal_type = request.POST.get('goal_type')
        goal.target_weight = request.POST.get('target_weight') or None
        goal.target_body_fat = request.POST.get('target_body_fat') or None
        goal.target_date = request.POST.get('target_date') or None
        goal.weekly_workout_goal = request.POST.get('weekly_workout_goal', 3)
        goal.weekly_calorie_goal = request.POST.get('weekly_calorie_goal', 2000)
        goal.is_active = True
        goal.save()
        
        messages.success(request, 'Fitness goal saved!')
        return redirect('tracking:dashboard')
    
    return render(request, 'tracking/set_goal.html', {'goal': goal})


@login_required
def bmi_calculator(request):
    """BMI Calculator tool"""
    # Require active membership to access BMI calculator
    has_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gte=dj_timezone.now()
    ).exists()

    if not has_membership:
        return render(request, 'tracking/membership_required.html')
    bmi = None
    category = None
    color = None
    advice = None
    
    if request.method == 'POST':
        height = float(request.POST.get('height'))
        weight = float(request.POST.get('weight'))
        
        height_in_meters = height / 100
        bmi = round(weight / (height_in_meters ** 2), 1)
        
        if bmi < 18.5:
            category = 'Underweight'
            color = 'yellow'
            advice = 'Consider a balanced diet with healthy calories and strength training.'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
            color = 'green'
            advice = 'Great job! Maintain your healthy lifestyle with balanced diet and regular exercise.'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            color = 'orange'
            advice = 'Focus on portion control, increase physical activity, and consult a nutritionist.'
        else:
            category = 'Obese'
            color = 'red'
            advice = 'Consult a healthcare provider. Start with low-impact exercises and diet modifications.'
    
    context = {
        'bmi': bmi,
        'category': category,
        'color': color,
        'advice': advice,
    }
    return render(request, 'tracking/bmi_calculator.html', context)


@login_required
def workout_log(request):
    """Log workout activity"""
    if request.method == 'POST':
        workout_log = WorkoutLog.objects.create(
            user=request.user,
            duration_minutes=request.POST.get('duration_minutes'),
            calories_burned=request.POST.get('calories_burned'),
            exercises_completed=request.POST.get('exercises_completed'),
            notes=request.POST.get('notes'),
            felt_difficulty=request.POST.get('felt_difficulty') or None,
        )
        messages.success(request, 'Workout logged successfully!')
        return redirect('tracking:dashboard')
    
    return render(request, 'tracking/workout_log.html')


def calculate_stats(user, progress_records):
    """Calculate user statistics"""
    stats = {
        'total_entries': progress_records.count(),
        'weight_change': 0,
        'avg_bmi': 0,
        'best_week': 0,
    }
    
    if progress_records.count() >= 2:
        first_weight = progress_records.last().weight
        current_weight = progress_records.first().weight
        stats['weight_change'] = round(current_weight - first_weight, 1)
    
    bmi_values = [p.bmi for p in progress_records if p.bmi]
    if bmi_values:
        stats['avg_bmi'] = round(sum(bmi_values) / len(bmi_values), 1)
    
    # Get workout stats
    workout_logs = WorkoutLog.objects.filter(user=user)[:30]
    stats['total_workouts'] = workout_logs.count()
    stats['total_calories'] = sum(w.calories_burned for w in workout_logs)
    stats['total_minutes'] = sum(w.duration_minutes for w in workout_logs)
    
    return stats