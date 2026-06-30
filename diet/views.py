from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import DietPlan, DietCategory, Meal, UserDietProgress


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


def diet_list(request):
    """Display diet plans based on membership level"""

    has_membership = request.user.is_authenticated and (
        request.user.is_staff or getattr(request.user, 'has_active_membership', lambda: False)()
    )
    if not has_membership:
        return render(request, 'diet/list.html', {
            'membership_required': True,
            'membership_alert_title': 'Membership Required',
            'membership_alert_message': 'You need an active membership to access diet plans. Choose a plan that best suits your fitness goals!',
        })

    categories = DietCategory.objects.filter(is_active=True)

    # Get user's membership level
    user_plan = None
    if getattr(request.user, 'has_active_membership', lambda: False)():
        current = getattr(request.user, 'current_membership', None)
        if not current:
            try:
                current = request.user.memberships.filter(status='active', end_date__gt=timezone.now()).first()
            except Exception:
                current = None
        if current:
            plan_type = getattr(current, 'plan_type', None)
            if not plan_type and hasattr(current, 'plan'):
                plan_type = getattr(current.plan, 'plan_type', None)
            user_plan = plan_type

    # Restrictions per plan type
    # Basic: Basic Diet Plans (limit 5)
    # Pro: Advanced Diet Plans (limit 15)
    # Premium: Custom Diet Plans (full access)
    def fetch_plans(goal, limit=None):
        qs = DietPlan.objects.filter(diet_goal=goal, is_active=True).order_by('-created_at')
        if limit:
            return list(qs[:limit])
        return list(qs)

    if user_plan == 'premium':
        weight_loss_plans = fetch_plans('weight_loss', limit=None)
        weight_gain_plans = fetch_plans('weight_gain', limit=None)
        muscle_gain_plans = fetch_plans('muscle_gain', limit=None)
        maintenance_plans = fetch_plans('maintenance', limit=None)
    elif user_plan == 'pro':
        weight_loss_plans = fetch_plans('weight_loss', limit=15)
        weight_gain_plans = fetch_plans('weight_gain', limit=15)
        muscle_gain_plans = fetch_plans('muscle_gain', limit=15)
        maintenance_plans = fetch_plans('maintenance', limit=15)
    else:  # Basic or unauthenticated users
        weight_loss_plans = fetch_plans('weight_loss', limit=5)
        weight_gain_plans = fetch_plans('weight_gain', limit=5)
        muscle_gain_plans = fetch_plans('muscle_gain', limit=5)
        maintenance_plans = fetch_plans('maintenance', limit=5)

    # Sort by day order
    DAY_ORDER = {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
        'sunday': 7,
    }

    weight_loss_plans = sorted(weight_loss_plans, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))
    weight_gain_plans = sorted(weight_gain_plans, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))
    muscle_gain_plans = sorted(muscle_gain_plans, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))
    maintenance_plans = sorted(maintenance_plans, key=lambda x: DAY_ORDER.get(getattr(x, 'day_of_week', '').lower(), 99))

    # Upgrade flow is transient per-request via ?upgrade=pro or ?upgrade=premium
    request_upgrade = request.GET.get('upgrade', '').lower()
    is_in_upgrade_flow = request_upgrade in {'pro', 'premium'}
    selected_upgrade_plan = request_upgrade
    is_target_selected = selected_upgrade_plan in {'pro', 'premium'}
    is_premium_selected = selected_upgrade_plan == 'premium'

    # Decide which upgrade banners to show.
    # Basic users should see both Pro and Premium banners. Pro users see Premium only.
    show_pro_banner = False
    show_premium_banner = False
    pro_action_url = reverse('membership:plans') + '?upgrade=pro'
    premium_action_url = reverse('membership:plans') + '?upgrade=premium'

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

    pro_message = "Upgrade to Pro for more diet plans and features!"
    premium_message = "Upgrade to Premium for full access to all diet plans!"
    is_upgrade_page = False
    is_checkout_page = False

    context = {
        'categories': categories,
        'weight_loss_plans': weight_loss_plans,
        'weight_gain_plans': weight_gain_plans,
        'muscle_gain_plans': muscle_gain_plans,
        'maintenance_plans': maintenance_plans,
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
    return render(request, 'diet/list.html', context)


def diet_detail(request, plan_id):
    """Display diet plan details - Membership required"""
    diet_plan = get_object_or_404(DietPlan, id=plan_id, is_active=True)

    if not request.user.is_authenticated or (not request.user.is_staff and not getattr(request.user, 'has_active_membership', lambda: False)()):
        return render(request, 'diet/detail.html', {
            'membership_required': True,
            'diet_plan': diet_plan,
        })

    # Get today's progress for this user
    today_progress = None
    if request.user.is_authenticated:
        today_progress = UserDietProgress.objects.filter(
            user=request.user,
            diet_plan=diet_plan,
            scheduled_date=timezone.now().date()
        ).first()

    # Calculate total nutrition
    nutrition = {
        'calories': getattr(diet_plan, 'total_calories', 0),
        'protein': getattr(diet_plan, 'total_protein', 0),
        'carbs': getattr(diet_plan, 'total_carbs', 0),
        'fats': getattr(diet_plan, 'total_fats', 0),
    }

    # Enforce plan-based access to diet details
    # Build allowed ids for this user's plan (same logic as list)
    def allowed_ids_for_user(plan_type):
        def ids_for(goal, limit=None):
            qs = DietPlan.objects.filter(diet_goal=goal, is_active=True).order_by('-created_at')
            if limit:
                return [p.id for p in qs[:limit]]
            return [p.id for p in qs]

        limits = {'basic': 5, 'pro': 15, 'premium': None}
        limit = limits.get(plan_type, 5)
        ids = []
        for g in ['weight_loss', 'weight_gain', 'muscle_gain', 'maintenance']:
            ids.extend(ids_for(g, limit))
        return set(ids)

    allowed_ids = set()
    if request.user.is_authenticated and getattr(request.user, 'has_active_membership', lambda: False)():
        # determine plan type similar to list
        current = getattr(request.user, 'current_membership', None)
        if not current:
            try:
                current = request.user.memberships.filter(status='active', end_date__gt=timezone.now()).first()
            except Exception:
                current = None
        if current:
            current_plan_type = getattr(current, 'plan_type', None) or getattr(current.plan, 'plan_type', None) if hasattr(current, 'plan') else None
        else:
            current_plan_type = None
        allowed_ids = allowed_ids_for_user(current_plan_type)

    # If the diet_plan is not in allowed set, block and suggest upgrade
    if allowed_ids and diet_plan.id not in allowed_ids:
        messages.info(request, 'This diet plan is available on higher membership tiers. Please upgrade to access it.')
        return redirect('membership:plans')

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
        meals = [getattr(todays_plan, 'breakfast', None), getattr(todays_plan, 'lunch', None), getattr(todays_plan, 'dinner', None), getattr(todays_plan, 'snack1', None), getattr(todays_plan, 'snack2', None)]
        for meal in meals:
            if meal and getattr(meal, 'ingredients', None):
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