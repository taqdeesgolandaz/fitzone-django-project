from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DietPlan, DietCategory, Meal, UserDietProgress
from accounts.decorators import membership_required

@membership_required
def diet_list(request):
    """Display all diet plans - Membership Required"""
    # ... your existing code

@membership_required
def diet_detail(request, plan_id):
    """Display diet plan details - Membership Required"""
    # ... your existing code

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

@login_required
def diet_list(request):
    """Display all diet plans - Login Required"""
    categories = DietCategory.objects.filter(is_active=True)
    
    # Get diet plans grouped by goal and sort by day order
    weight_loss_plans = DietPlan.objects.filter(diet_goal='weight_loss', is_active=True)
    weight_loss_plans = sorted(weight_loss_plans, key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    
    weight_gain_plans = DietPlan.objects.filter(diet_goal='weight_gain', is_active=True)
    weight_gain_plans = sorted(weight_gain_plans, key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    
    muscle_gain_plans = DietPlan.objects.filter(diet_goal='muscle_gain', is_active=True)
    muscle_gain_plans = sorted(muscle_gain_plans, key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    
    maintenance_plans = DietPlan.objects.filter(diet_goal='maintenance', is_active=True)
    maintenance_plans = sorted(maintenance_plans, key=lambda x: DAY_ORDER.get(x.day_of_week, 99))
    
    context = {
        'categories': categories,
        'weight_loss_plans': weight_loss_plans,
        'weight_gain_plans': weight_gain_plans,
        'muscle_gain_plans': muscle_gain_plans,
        'maintenance_plans': maintenance_plans,
    }
    return render(request, 'diet/list.html', context)


@login_required
def diet_detail(request, plan_id):
    """Display diet plan details - Login Required"""
    diet_plan = get_object_or_404(DietPlan, id=plan_id, is_active=True)
    
    # Get today's progress for this user
    today_progress = None
    if request.user.is_authenticated:
        today_progress = UserDietProgress.objects.filter(
            user=request.user,
            diet_plan=diet_plan,
            scheduled_date=timezone.now().date()
        )
    
    # Calculate total nutrition
    nutrition = {
        'calories': diet_plan.total_calories,
        'protein': diet_plan.total_protein,
        'carbs': diet_plan.total_carbs,
        'fats': diet_plan.total_fats,
    }
    
    context = {
        'diet_plan': diet_plan,
        'today_progress': today_progress,
        'nutrition': nutrition,
    }
    return render(request, 'diet/detail.html', context)


@login_required
def track_meal(request, progress_id):
    """Mark meal as completed"""
    progress = get_object_or_404(UserDietProgress, id=progress_id, user=request.user)
    
    if request.method == 'POST':
        progress.status = 'completed'
        progress.completed_at = timezone.now()
        progress.notes = request.POST.get('notes', '')
        progress.save()
        
        messages.success(request, f'Great! You completed {progress.get_meal_type_display()}!')
        return redirect('diet:detail', plan_id=progress.diet_plan.id)
    
    return render(request, 'diet/track.html', {'progress': progress})


@login_required
def my_diet_progress(request):
    """Show user's diet progress"""
    progress_records = UserDietProgress.objects.filter(
        user=request.user
    ).order_by('-scheduled_date')[:30]
    
    # Calculate statistics
    total_meals = progress_records.count()
    completed_meals = progress_records.filter(status='completed').count()
    
    stats = {
        'total_meals': total_meals,
        'completed_meals': completed_meals,
        'completion_rate': int((completed_meals / total_meals * 100)) if total_meals > 0 else 0,
        'total_calories': sum(p.meal.calories for p in progress_records if p.status == 'completed' and p.meal) if progress_records else 0,
    }
    
    context = {
        'progress_records': progress_records,
        'stats': stats,
    }
    return render(request, 'diet/progress.html', context)


@login_required
def shopping_list(request):
    """Generate shopping list based on user's diet plan"""
    today = timezone.now().date()
    todays_plan = DietPlan.objects.filter(
        day_of_week=today.strftime('%A').lower(),
        is_active=True
    ).first()
    
    ingredients = []
    if todays_plan:
        meals = [todays_plan.breakfast, todays_plan.lunch, todays_plan.dinner, todays_plan.snack1, todays_plan.snack2]
        for meal in meals:
            if meal and meal.ingredients:
                for line in meal.ingredients.split('\n'):
                    if line.strip():
                        ingredients.append(line.strip())
    
    # Remove duplicates
    ingredients = list(dict.fromkeys(ingredients))
    
    context = {
        'ingredients': ingredients,
        'diet_plan': todays_plan,
    }
    return render(request, 'diet/shopping_list.html', context)