from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .models import MembershipPlan, UserMembership
from payments.models import BankAccount, Payment

import sys
import uuid

def get_razorpay_client():
    try:
        import razorpay
    except ImportError as exc:
        print(f'Razorpay package import failed in membership views: {exc}', file=sys.stderr)
        return None

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        print(f'Razorpay API keys are missing in membership views. ID set: {bool(settings.RAZORPAY_KEY_ID)}, secret set: {bool(settings.RAZORPAY_KEY_SECRET)}', file=sys.stderr)
        return None

    def safe_create_order(client, order_data, context=''):
        try:
            return client.order.create(data=order_data)
        except Exception as exc:
            err_type = type(exc)
            print(f'Razorpay order creation error ({context}) in membership views: {err_type.__name__}: {exc}', file=sys.stderr)
            if 'Authentication' in str(exc) or 'auth' in str(exc).lower():
                print('HINT: Authentication failed. Verify RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are correct and active.', file=sys.stderr)
            raise

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        secret_mask = 'SET' if settings.RAZORPAY_KEY_SECRET else 'NOT SET'
        print(f'Razorpay client initialized in membership views: {settings.RAZORPAY_KEY_ID}, secret {secret_mask}', file=sys.stderr)
        return client
    except Exception as exc:
        print(f'Razorpay client initialization failed in membership views: {exc}', file=sys.stderr)
        return None


def plans_view(request):
    """View all membership plans"""
    plans = MembershipPlan.objects.filter(is_active=True)
    
    # Get user's current membership if logged in
    current_membership = None
    if request.user.is_authenticated:
        current_membership = UserMembership.objects.filter(
            user=request.user, 
            status='active',
            end_date__gt=timezone.now()
        ).first()

    # Use transient URL parameter '?upgrade=pro' or '?upgrade=premium' to indicate
    # an upgrade selection for this request only. Do NOT persist selection in session.
    selected_upgrade_plan = request.GET.get('upgrade', '').lower()
    if selected_upgrade_plan not in {'pro', 'premium'}:
        selected_upgrade_plan = ''

    is_upgrade_flow = bool(selected_upgrade_plan)
    is_premium_selected = selected_upgrade_plan == 'premium'

    # Do not show transient selection messages on the plans page.
    # The UI highlights the selected card via `selected_upgrade_plan`; no banner message needed.
    selection_message = None

    context = {
        'plans': plans,
        'current_membership': current_membership,
        'selected_upgrade_plan': selected_upgrade_plan,
        'is_premium_selected': is_premium_selected,
        'is_upgrade_page': False,
        'is_checkout_page': False,
        'is_in_upgrade_flow': is_upgrade_flow,
        'show_upgrade_banner': False,
        'selection_message': selection_message,
    }
    return render(request, 'membership/plans.html', context)


@login_required
def process_upgrade(request):
    """Store selected plan id in session and redirect to payments upgrade flow."""
    plan_id = request.GET.get('plan_id') or request.POST.get('plan_id')
    if plan_id:
        # Redirect to payments upgrade flow with plan_id as a query parameter (transient)
        return redirect(f"{reverse('payments:upgrade_membership')}?plan_id={plan_id}")
    return redirect('membership:plans')

@login_required
def purchase_plan(request, plan_id):
    """Purchase a membership plan"""
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    
    # Check if user already has active membership
    active_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if active_membership:
        messages.warning(request, 'You already have an active membership. Let it expire or cancel it first.')
        return redirect('membership:plans')
    
    if request.method == 'POST':
        # Calculate end date
        end_date = timezone.now() + timezone.timedelta(days=plan.get_duration_days())
        
        # Create membership (payment will be integrated later)
        membership = UserMembership.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date,
            amount_paid=plan.price,
            status='active'
        )
        
        # Update user's membership status
        request.user.current_membership = plan
        request.user.membership_expiry = end_date
        request.user.membership_active = True
        request.user.save()
        
        # do not persist selection in session; nothing to pop
        messages.success(request, f'Successfully purchased {plan.name} plan! Your membership is active until {end_date.date()}.')
        return redirect('membership:my_membership')
    
    bank_account = BankAccount.objects.filter(is_active=True, is_verified=True).first()
    payee_name = bank_account.account_holder_name.strip() if bank_account and bank_account.account_holder_name else 'FitZone'

    context = {
        'plan': plan,
        'duration_days': plan.get_duration_days(),
    }

    # Create a Razorpay order so the purchase page can open Checkout directly
    client = get_razorpay_client()
    if client is not None:
        try:
            amount_paise = int(float(plan.price) * 100)
            order_data = {
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'membership_{plan.id}_{request.user.id}_{uuid.uuid4().hex[:8]}',
                'payment_capture': 1,
                'notes': {
                    'user_id': request.user.id,
                    'plan_id': plan.id,
                    'type': 'membership',
                }
            }
            razorpay_order = safe_create_order(client, order_data, context='purchase_plan')

            # Create pending Payment record
            payment = Payment.objects.create(
                user=request.user,
                amount=plan.price,
                razorpay_order_id=razorpay_order['id'],
                status='pending',
                transaction_id=f'MEM{plan.id}_{uuid.uuid4().hex[:8].upper()}'
            )

            context.update({
                'razorpay_order': razorpay_order,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
            })
        except Exception as e:
            messages.error(request, f'Unable to initialize payment: {e}')

    return render(request, 'membership/purchase.html', context)

@login_required
def upgrade_membership(request, plan_id):
    """Upgrade membership to a higher tier"""
    new_plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    
    # Check if user has active membership
    active_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if not active_membership:
        messages.error(request, 'You do not have an active membership to upgrade.')
        return redirect('membership:plans')
    
    current_plan = active_membership.plan
    
    # Check if it's an upgrade (not same tier or downgrade)
    if new_plan.plan_type == current_plan.plan_type:
        messages.info(request, 'You already have this plan.')
        return redirect('membership:plans')
    
    if not current_plan.is_upgrade_to(new_plan):
        messages.warning(request, 'You can only upgrade to a higher tier.')
        return redirect('membership:plans')
    
    if request.method == 'POST':
        # Calculate prorated upgrade cost
        days_remaining = active_membership.days_remaining()
        
        # Cost per day for current and new plan
        current_plan_days = current_plan.get_duration_days()
        new_plan_days = new_plan.get_duration_days()
        
        current_daily_rate = float(current_plan.price) / current_plan_days
        new_daily_rate = float(new_plan.price) / new_plan_days
        
        # Calculate upgrade cost for remaining days
        current_remaining_cost = current_daily_rate * days_remaining
        new_remaining_cost = new_daily_rate * days_remaining
        
        upgrade_amount = new_remaining_cost - current_remaining_cost
        upgrade_amount = max(0, round(upgrade_amount, 2))  # Ensure non-negative
        
        # Create new membership with end date extended from current
        new_end_date = active_membership.end_date + timezone.timedelta(days=new_plan_days)
        
        new_membership = UserMembership.objects.create(
            user=request.user,
            plan=new_plan,
            start_date=timezone.now(),
            end_date=new_end_date,
            amount_paid=upgrade_amount,
            status='active'
        )
        
        # Cancel old membership
        active_membership.status = 'cancelled'
        active_membership.save()
        
        # Update user's membership status
        request.user.current_membership = new_plan
        request.user.membership_expiry = new_end_date
        request.user.membership_active = True
        request.user.save()
        
        messages.success(request, f'Successfully upgraded to {new_plan.name}! Your new membership is valid until {new_end_date.date()}.')
        return redirect('membership:my_membership')
    
    # Calculate prorated cost for display
    days_remaining = active_membership.days_remaining()
    current_plan_days = current_plan.get_duration_days()
    new_plan_days = new_plan.get_duration_days()
    
    current_daily_rate = float(current_plan.price) / current_plan_days
    new_daily_rate = float(new_plan.price) / new_plan_days
    
    current_remaining_cost = current_daily_rate * days_remaining
    new_remaining_cost = new_daily_rate * days_remaining
    
    upgrade_amount = max(0, round(new_remaining_cost - current_remaining_cost, 2))
    
    bank_account = BankAccount.objects.filter(is_active=True, is_verified=True).first()
    payee_name = bank_account.account_holder_name.strip() if bank_account and bank_account.account_holder_name else 'FitZone'

    context = {
        'current_plan': current_plan,
        'new_plan': new_plan,
        'active_membership': active_membership,
        'days_remaining': days_remaining,
        'upgrade_amount': upgrade_amount,
        'new_end_date': active_membership.end_date + timezone.timedelta(days=new_plan_days),
    }

    # Create a Razorpay order if upgrade cost > 0
    client = get_razorpay_client()
    if client is not None and upgrade_amount > 0:
        try:
            amount_paise = int(float(upgrade_amount) * 100)
            # Razorpay minimum amount is 100 paise (₹1). If below minimum, treat as free upgrade.
            if amount_paise < 100:
                # Treat as free upgrade on the UI (no payment required)
                upgrade_amount = 0
            else:
                order_data = {
                    'amount': amount_paise,
                    'currency': 'INR',
                    'receipt': f'upgrade_{current_plan.id}_to_{new_plan.id}_{request.user.id}_{uuid.uuid4().hex[:8]}',
                    'payment_capture': 1,
                    'notes': {
                        'user_id': request.user.id,
                        'current_plan_id': current_plan.id,
                        'new_plan_id': new_plan.id,
                        'type': 'upgrade',
                    }
                }
                razorpay_order = safe_create_order(client, order_data, context='upgrade_membership')

                # Create pending Payment record
                payment = Payment.objects.create(
                    user=request.user,
                    amount=upgrade_amount,
                    razorpay_order_id=razorpay_order['id'],
                    status='pending',
                    transaction_id=f'UPG{current_plan.id}_{new_plan.id}_{uuid.uuid4().hex[:8].upper()}'
                )

                context.update({
                    'razorpay_order': razorpay_order,
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                })
        except Exception as e:
            messages.error(request, f'Unable to initialize payment: {e}')

    return render(request, 'membership/upgrade.html', context)


@login_required
def my_membership_view(request):
    """View user's current membership"""
    active_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    expired_memberships = UserMembership.objects.filter(
        user=request.user
    ).exclude(id=active_membership.id if active_membership else None)[:5]
    
    context = {
        'active_membership': active_membership,
        'expired_memberships': expired_memberships,
    }
    return render(request, 'membership/my_membership.html', context)