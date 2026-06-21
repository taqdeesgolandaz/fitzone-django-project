from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MembershipPlan, UserMembership
from payments.models import BankAccount

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
    
    context = {
        'plans': plans,
        'current_membership': current_membership,
    }
    return render(request, 'membership/plans.html', context)

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
        
        messages.success(request, f'Successfully purchased {plan.name} plan! Your membership is active until {end_date.date()}.')
        return redirect('membership:my_membership')
    
    bank_account = BankAccount.objects.filter(is_active=True, is_verified=True).first()
    upi_id = bank_account.upi_id.strip() if bank_account and bank_account.upi_id else ''
    payee_name = bank_account.account_holder_name.strip() if bank_account and bank_account.account_holder_name else 'FitZone'

    context = {
        'plan': plan,
        'duration_days': plan.get_duration_days(),
        'upi_id': upi_id,
        'payee_name': payee_name,
    }
    return render(request, 'membership/purchase.html', context)

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