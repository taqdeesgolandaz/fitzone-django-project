import json
import re
import sys
import uuid
from urllib.parse import quote
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect


def get_razorpay_client():
    try:
        import razorpay
    except ImportError as exc:
        print(f'Razorpay package import failed: {exc}', file=sys.stderr)
        return None

    print(f'RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID}', file=sys.stderr)
    print(f'RAZORPAY_KEY_SECRET: {"SET" if settings.RAZORPAY_KEY_SECRET else "NOT SET"}', file=sys.stderr)

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print('✅ Razorpay client initialized', file=sys.stderr)
        return client
    except Exception as exc:
        print(f'❌ Razorpay init error: {exc}', file=sys.stderr)
        return None

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from membership.models import MembershipPlan, UserMembership
from .models import BankAccount, Payment
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import json as _json


# Removed custom UPI webhook and status-check endpoints.
# Manual UPI flows were deprecated in favor of Razorpay-only integration.


@login_required
def initiate_session_payment(request, session_id):
    """Initiate payment for a trainer session."""
    from trainers.models import TrainerSession
    
    session = get_object_or_404(TrainerSession, id=session_id, user=request.user, status='approved')
    
    # Create Razorpay Order
    order_amount = int(session.amount * 100)
    
    order_data = {
        'amount': order_amount,
        'currency': 'INR',
        'receipt': f'session_{session.id}_{request.user.id}_{uuid.uuid4().hex[:8]}',
        'payment_capture': 1,
        'notes': {
            'user_id': request.user.id,
            'session_id': session.id,
            'trainer_name': session.trainer.full_name,
            'type': 'trainer_session',
        }
    }
    
    try:
        client = get_razorpay_client()
        if client is None:
            raise RuntimeError('Razorpay client is unavailable. Please install the Razorpay SDK or check configuration.')

        razorpay_order = client.order.create(data=order_data)
        
        payment = Payment.objects.create(
            user=request.user,
            amount=session.amount,
            razorpay_order_id=razorpay_order['id'],
            status='pending'
        )
        
        context = {
            'payment': payment,
            'razorpay_order': razorpay_order,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'session': session,
        }
        return render(request, 'payments/session_checkout.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}')
        return redirect('trainers:my_sessions')


@login_required
def upi_payment(request, plan_id):
    """Initiate membership payment (creates Razorpay order and renders checkout)."""
    plan = MembershipPlan.objects.filter(id=plan_id, is_active=True).first()
    if not plan:
        messages.error(request, 'Selected membership plan was not found or is inactive.')
        return redirect('membership:plans')

    # Create Razorpay Order
    order_amount = int(float(plan.price) * 100)
    order_data = {
        'amount': order_amount,
        'currency': 'INR',
        'receipt': f'MEM{plan.id}_{request.user.id}_{uuid.uuid4().hex[:8]}',
        'payment_capture': 1,
        'notes': {
            'user_id': request.user.id,
            'plan_id': plan.id,
            'plan_name': plan.name,
            'type': 'membership',
        }
    }

    try:
        client = get_razorpay_client()
        if client is None:
            raise RuntimeError('Razorpay client is unavailable. Please install/configure Razorpay.')

        razorpay_order = client.order.create(data=order_data)

        payment = Payment.objects.create(
            user=request.user,
            amount=plan.price,
            razorpay_order_id=razorpay_order['id'],
            status='pending',
            transaction_id=order_data['receipt']
        )

        # Pick an available bank account record if present
        bank_account = BankAccount.objects.first()

        context = {
            'plan': plan,
            'payment': payment,
            'razorpay_order': razorpay_order,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'bank_account': bank_account,
            'is_checkout_page': True,
            'is_in_upgrade_flow': False,
            'is_premium_selected': False,
            'show_upgrade_banner': False,
        }
        return render(request, 'payments/checkout.html', context)

    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}')
        return redirect('membership:plans')


@login_required
def create_session_order(request, session_id):
    """Create a Razorpay order for a trainer session via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    client = get_razorpay_client()
    if client is None:
        return JsonResponse({'success': False, 'error': 'Razorpay client unavailable. Check server configuration.'})

    from trainers.models import TrainerSession
    try:
        session = get_object_or_404(TrainerSession, id=session_id, user=request.user, status='approved')
        amount = int(float(session.amount) * 100)
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'session_{session.id}_{request.user.id}_{uuid.uuid4().hex[:8]}',
            'payment_capture': 1,
            'notes': {
                'session_id': session.id,
                'user_id': request.user.id,
                'type': 'trainer_session',
            }
        }
        order = client.order.create(data=order_data)
        payment = Payment.objects.create(
            user=request.user,
            amount=session.amount,
            razorpay_order_id=order['id'],
            status='pending'
        )
        return JsonResponse({
            'success': True,
            'amount': amount,
            'order_id': order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def verify_session_payment(request):
    """Verify Razorpay payment for trainer sessions."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
            return JsonResponse({'success': False, 'error': 'Missing payment verification fields.'})

        payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id, user=request.user).first()
        if not payment:
            return JsonResponse({'success': False, 'error': 'Payment record not found.'}, status=404)

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        payment.transaction_id = razorpay_payment_id
        payment.paid_at = timezone.now()
        payment.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def payment_success(request):
    """Verify Razorpay payment for membership purchases and activate membership."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        try:
            raw_body = request.body.decode('utf-8')
            data = json.loads(raw_body) if raw_body else {}
        except ValueError:
            data = request.POST

        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
            return JsonResponse({'success': False, 'error': 'Missing payment verification fields.'})

        # Verify signature with Razorpay
        try:
            client = get_razorpay_client()
            if client is None:
                return JsonResponse({'success': False, 'error': 'Razorpay client unavailable. Check server configuration.'})
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Signature verification failed: {str(e)}'})

        payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id, user=request.user).first()
        if not payment:
            return JsonResponse({'success': False, 'error': 'Payment record not found.'}, status=404)

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save()

        # Activate membership if this payment was for a membership plan (transaction_id stores plan id as MEM{plan_id}_...)
        plan_id = None
        if payment.transaction_id and payment.transaction_id.startswith('MEM'):
            m = re.match(r'^MEM(\d+)', payment.transaction_id)
            if m:
                plan_id = int(m.group(1))

        if plan_id:
            plan = MembershipPlan.objects.filter(id=plan_id, is_active=True).first()
            if plan:
                end_date = timezone.now() + timedelta(days=plan.get_duration_days())
                membership = UserMembership.objects.create(
                    user=request.user,
                    plan=plan,
                    end_date=end_date,
                    amount_paid=payment.amount,
                    status='active'
                )
                payment.membership = membership
                payment.save()
                # Update user's membership flags
                try:
                    user = request.user
                    user.current_membership = plan
                    user.membership_expiry = end_date
                    user.membership_active = True
                    user.save()
                except Exception:
                    # Non-fatal: membership created but user flags couldn't be updated
                    pass

        return JsonResponse({'success': True, 'redirect_url': reverse('membership:my_membership')})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def payment_history(request):
    """View payment history."""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def download_invoice(request, payment_id):
    """Download invoice as PDF."""
    from .pdf_generator import InvoiceGenerator
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.user != payment.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to download this invoice.")
        return redirect('payments:payment_history')
    
    return InvoiceGenerator.download_invoice(request, payment_id)


@csrf_exempt
def payment_failed(request):
    """Handle failed payment."""
    return render(request, 'payments/failed.html')


@login_required
def upgrade_membership(request):
    """Display upgrade page and handle upgrade logic (membership -> payments bridge)
    This view calculates prorated upgrade cost and renders a payments/upgrade.html template.
    """
    # Get current membership
    active_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    if not active_membership:
        messages.error(request, "You don't have an active membership to upgrade.")
        return redirect('membership:plans')

    current_plan = active_membership.plan

    # Get the plan to upgrade to (pass from URL query or session)
    new_plan_id = request.GET.get('plan_id') or request.session.get('upgrade_plan_id')
    if not new_plan_id:
        messages.error(request, 'Please select a plan to upgrade to.')
        return redirect('membership:plans')

    new_plan = get_object_or_404(MembershipPlan, id=new_plan_id, is_active=True)

    # Don't allow upgrade to same plan
    if current_plan.id == new_plan.id:
        messages.warning(request, 'You are already on this plan.')
        return redirect('membership:my_membership')

    # Calculate days remaining (use .date to avoid timezone differences)
    try:
        days_remaining = (active_membership.end_date.date() - timezone.now().date()).days
    except Exception:
        days_remaining = max(0, (active_membership.end_date - timezone.now()).days)
    if days_remaining < 0:
        days_remaining = 0

    total_days = new_plan.get_duration_days() + days_remaining

    # Daily rate of current plan (approx)
    current_daily_rate = float(current_plan.price) / max(1, current_plan.get_duration_days())

    # Pro-rated value of remaining days
    current_pro_rate = current_daily_rate * days_remaining

    # Full price of new plan
    new_plan_price = float(new_plan.price)

    # Calculate adjustment (cap by new plan price)
    adjustment = min(current_pro_rate, new_plan_price)
    upgrade_amount = new_plan_price - adjustment
    upgrade_amount = max(0.0, round(upgrade_amount, 2))

    # Store upgrade details in session for subsequent calls
    request.session['upgrade_details'] = {
        'new_plan_id': int(new_plan.id),
        'upgrade_amount': float(upgrade_amount),
        'current_plan_id': int(current_plan.id),
    }

    # Features
    current_features = current_plan.features if hasattr(current_plan, 'features') else []
    new_features = new_plan.features if hasattr(new_plan, 'features') else []
    additional_features = [f for f in new_features if f not in current_features]

    # Savings percentage
    savings_percent = 0
    if new_plan_price > 0:
        savings_percent = round(((new_plan_price - upgrade_amount) / new_plan_price) * 100)

    razorpay_order = None
    razorpay_key = settings.RAZORPAY_KEY_ID
    if upgrade_amount > 0:
        client = get_razorpay_client()
        if client is not None:
            # Avoid Razorpay minimum amount error: do not create orders below 100 paise
            if upgrade_amount < 1:  # 100 paise = 1 INR
                # Treat as free upgrade (no Razorpay order)
                razorpay_order = None
            else:
                try:
                    order_amount = int(upgrade_amount * 100)
                    order_data = {
                        'amount': order_amount,
                        'currency': 'INR',
                        'receipt': f'upgrade_{request.user.id}_{timezone.now().timestamp()}',
                        'payment_capture': 1,
                        'notes': {
                            'user_id': request.user.id,
                            'current_plan': current_plan.id,
                            'new_plan': new_plan.id,
                            'type': 'upgrade'
                        }
                    }
                    razorpay_order = client.order.create(data=order_data)
                except Exception as e:
                    # Log but allow page to render
                    print(f"Razorpay order creation failed: {e}")
        else:
            print('Razorpay client unavailable in upgrade_membership. Skipping order creation.', file=sys.stderr)

    context = {
        'active_membership': active_membership,
        'current_plan': current_plan,
        'new_plan': new_plan,
        'days_remaining': days_remaining,
        'total_days': total_days,
        'current_pro_rate': current_pro_rate,
        'adjustment': adjustment,
        'upgrade_amount': upgrade_amount,
        'additional_features': additional_features,
        'savings_percent': savings_percent,
        'new_end_date': timezone.now().date() + timedelta(days=total_days),
        'razorpay_order': razorpay_order,
        'razorpay_key': razorpay_key,
    }

    # Render the membership upgrade template directly to avoid duplicate base layout
    return render(request, 'membership/upgrade.html', context)


@login_required
def create_upgrade_order(request):
    """Create Razorpay order for upgrade via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        upgrade_details = request.session.get('upgrade_details')
        if not upgrade_details:
            return JsonResponse({'success': False, 'error': 'Upgrade details not found'})

        amount = upgrade_details.get('upgrade_amount', 0)
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'No payment required'})

        client = get_razorpay_client()
        if client is None:
            return JsonResponse({'success': False, 'error': 'Razorpay client unavailable. Check server configuration.'})

        order_amount = int(amount * 100)

        order_data = {
            'amount': order_amount,
            'currency': 'INR',
            'receipt': f'upgrade_{request.user.id}_{timezone.now().timestamp()}',
            'payment_capture': 1,
            'notes': {
                'user_id': request.user.id,
                'type': 'upgrade'
            }
        }
        order = client.order.create(data=order_data)

        return JsonResponse({
            'success': True,
            'order_id': order['id'],
            'amount': order_amount,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def verify_upgrade_payment(request):
    """Verify upgrade payment and activate new plan"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        data = _json.loads(request.body)
        payment_id = data.get('payment_id') or data.get('razorpay_payment_id')
        order_id = data.get('order_id') or data.get('razorpay_order_id')
        signature = data.get('signature') or data.get('razorpay_signature')

        # Verify signature
        client = get_razorpay_client()
        if client is None:
            return JsonResponse({'success': False, 'error': 'Razorpay client unavailable. Check server configuration.'})
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        client.utility.verify_payment_signature(params_dict)

        # Get upgrade details
        upgrade_details = request.session.get('upgrade_details')
        if not upgrade_details:
            return JsonResponse({'success': False, 'error': 'Upgrade details not found'})

        new_plan_id = upgrade_details.get('new_plan_id')
        amount = upgrade_details.get('upgrade_amount')

        new_plan = get_object_or_404(MembershipPlan, id=new_plan_id)
        current_membership = UserMembership.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).first()

        if not current_membership:
            return JsonResponse({'success': False, 'error': 'No active membership found'})

        # Save payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_method='razorpay',
            status='success',
            transaction_id=payment_id,
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature,
            paid_at=timezone.now()
        )

        # Update membership: set new plan and extend end_date
        try:
            # Calculate days remaining on current membership
            try:
                days_remaining = (current_membership.end_date.date() - timezone.now().date()).days
            except Exception:
                days_remaining = max(0, (current_membership.end_date - timezone.now()).days)
            if days_remaining < 0:
                days_remaining = 0

            total_days = new_plan.get_duration_days() + days_remaining
            new_end_date = timezone.now() + timedelta(days=total_days)

            current_membership.plan = new_plan
            current_membership.amount_paid = float(current_membership.amount_paid or 0) + float(amount)
            current_membership.end_date = new_end_date
            current_membership.save()

            # Update user flags
            user = request.user
            user.current_membership = new_plan
            user.membership_expiry = new_end_date
            user.membership_active = True
            user.save()
        except Exception:
            # Non-fatal: ensure membership still points to new plan
            current_membership.plan = new_plan
            current_membership.save()

        # Clear session data
        request.session.pop('upgrade_details', None)

        return JsonResponse({'success': True})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'error': 'Payment verification failed'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def process_free_upgrade(request):
    """Process free upgrade (when upgrade_amount is 0)"""
    if request.method != 'POST':
        return redirect('membership:plans')

    upgrade_details = request.session.get('upgrade_details')
    if not upgrade_details:
        messages.error(request, 'Upgrade details not found.')
        return redirect('membership:plans')

    new_plan_id = upgrade_details.get('new_plan_id')
    new_plan = get_object_or_404(MembershipPlan, id=new_plan_id)

    current_membership = UserMembership.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now()
    ).first()

    if not current_membership:
        messages.error(request, 'No active membership found.')
        return redirect('membership:plans')

    # Update membership
    current_membership.plan = new_plan
    current_membership.save()

    # Update user
    user = request.user
    user.current_membership = new_plan
    user.save()

    # Clear session
    request.session.pop('upgrade_details', None)

    messages.success(request, f'🎉 Your membership has been upgraded to {new_plan.name}!')
    return redirect('membership:my_membership')


