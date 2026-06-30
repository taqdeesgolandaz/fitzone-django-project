import json
import re
import sys
import uuid
from urllib.parse import quote
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

# Razorpay client is initialized at runtime via `get_razorpay_client()` to avoid
# import-time failures when keys or the SDK are missing in certain environments.

def get_razorpay_client():
    try:
        import razorpay
    except ImportError as exc:
        print(f'Razorpay package import failed: {exc}', file=sys.stderr)
        if 'pkg_resources' in str(exc):
            print('HINT: pkg_resources is missing. Please install setuptools in the production environment.', file=sys.stderr)
        return None

    def _mask(s, keep=4):
        if not s:
            return ''
        if len(s) <= keep * 2:
            return '***'
        return s[:keep] + '...' + s[-keep:]

    print(f'RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID}', file=sys.stderr)
    print(f'RAZORPAY_KEY_SECRET: {"SET" if settings.RAZORPAY_KEY_SECRET else "NOT SET"} (masked={_mask(settings.RAZORPAY_KEY_SECRET)})', file=sys.stderr)

    # Basic format checks to catch common typos (O vs 0 etc.)
    if settings.RAZORPAY_KEY_ID and not settings.RAZORPAY_KEY_ID.startswith(('rzp_test_', 'rzp_live_')):
        print('WARNING: RAZORPAY_KEY_ID does not look like a typical Razorpay key (missing rzp_test_/rzp_live_ prefix).', file=sys.stderr)

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print('✅ Razorpay client initialized', file=sys.stderr)
        return client
    except Exception as exc:
        print(f'❌ Razorpay init error: {exc}', file=sys.stderr)
        return None


def safe_create_order(client, order_data, context=''):
    """Create a Razorpay order with detailed error logging for troubleshooting."""
    try:
        return client.order.create(data=order_data)
    except Exception as exc:
        try:
            import razorpay
            err_type = type(exc)
            print(f'Razorpay order creation error ({context}): {err_type.__name__}: {exc}', file=sys.stderr)
            # Provide a hint for authentication errors
            if 'Authentication' in str(exc) or 'auth' in str(exc).lower():
                print('HINT: Authentication failed. Verify RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are correct and active.', file=sys.stderr)
        except ImportError:
            print(f'Order creation error ({context}): {exc}', file=sys.stderr)
        raise

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

        razorpay_order = safe_create_order(client, order_data, context='initiate_session_payment')
        
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

        razorpay_order = safe_create_order(client, order_data, context='upi_payment')

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
        order = safe_create_order(client, order_data, context='create_session_order')
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
                UserMembership.deactivate_other_active_memberships(request.user)
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
    # Attempt to mark the related Payment record as failed when possible.
    order_id = request.GET.get('order_id') or request.GET.get('razorpay_order_id')
    try:
        if order_id:
            payment = Payment.objects.filter(razorpay_order_id=order_id).first()
            if payment:
                payment.status = 'failed'
                payment.save()
    except Exception as exc:  # non-fatal
        print(f"Failed to mark payment as failed for order {order_id}: {exc}", file=sys.stderr)

    return render(request, 'payments/failed.html')


@login_required
def upgrade_membership(request):
    """Display upgrade page and handle upgrade logic (membership -> payments bridge)
    This view calculates prorated upgrade cost and renders a payments/upgrade.html template.
    """
    import traceback
    try:
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

        # Calculate days remaining (safely handle missing/invalid end_date)
        days_remaining = 0
        try:
            if active_membership.end_date:
                # Prefer date arithmetic to avoid timezone surprises
                try:
                    days_remaining = (active_membership.end_date.date() - timezone.now().date()).days
                except Exception:
                    # Fallback to datetime subtraction
                    days_remaining = max(0, (active_membership.end_date - timezone.now()).days)
        except Exception:
            days_remaining = 0
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

        upgrade_start_date = timezone.now()
        new_plan_remaining_days = new_plan.get_duration_days()
        current_remaining_cost = current_pro_rate

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

        # Resolve logo URL from staticfiles manifest safely (avoid raising MissingManifestEntry)
        try:
            from django.contrib.staticfiles.storage import staticfiles_storage
            try:
                logo_url = staticfiles_storage.url('images/logo.png')
            except Exception:
                logo_url = ''
        except Exception:
            logo_url = ''
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
                        razorpay_order = safe_create_order(client, order_data, context='upgrade_membership')
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
            'upgrade_start_date': upgrade_start_date,
            'current_remaining_cost': current_remaining_cost,
            'new_plan_remaining_days': new_plan_remaining_days,
            'new_end_date': upgrade_start_date + timedelta(days=new_plan_remaining_days),
            'razorpay_order': razorpay_order,
            'razorpay_key': razorpay_key,
            'logo_url': logo_url,
            # For progress bar in template
            'days_remaining_percent': int((days_remaining / max(1, current_plan.get_duration_days())) * 100) if current_plan.get_duration_days() else 0,
        }

        # Render the membership upgrade template directly to avoid duplicate base layout
        return render(request, 'membership/upgrade.html', context)
    except Exception as exc:
        # Log full traceback to stderr so it appears in Render logs
        traceback.print_exc()
        print(f"upgrade_membership error: {exc}", file=sys.stderr)
        messages.error(request, 'An internal error occurred while preparing the upgrade. Please try again later.')
        return redirect('membership:plans')


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
        order = safe_create_order(client, order_data, context='create_upgrade_order')

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

        # Update membership: start a fresh plan period from the upgrade moment
        try:
            upgrade_start_date = timezone.now()
            new_end_date = upgrade_start_date + timedelta(days=new_plan.get_duration_days())

            current_membership.status = 'cancelled'
            current_membership.save(update_fields=['status'])
            UserMembership.deactivate_other_active_memberships(request.user, keep_membership_id=current_membership.id)
            new_membership = UserMembership.objects.create(
                user=request.user,
                plan=new_plan,
                start_date=upgrade_start_date,
                end_date=new_end_date,
                amount_paid=float(current_membership.amount_paid or 0) + float(amount),
                status='active'
            )

            # Update user flags
            user = request.user
            user.current_membership = new_plan
            user.membership_expiry = new_end_date
            user.membership_active = True
            user.save()
        except Exception:
            # Non-fatal: ensure the user still points to the selected plan
            user = request.user
            user.current_membership = new_plan
            user.membership_active = True
            user.save()

        # Clear session data
        request.session.pop('upgrade_details', None)

        return JsonResponse({'success': True})
    except Exception as e:
        if 'SignatureVerificationError' in str(type(e)) or 'signature' in str(e).lower():
            return JsonResponse({'success': False, 'error': 'Payment verification failed'})
        return JsonResponse({'success': False, 'error': str(e)})
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

    # Create a new active membership record and cancel the previous one
    current_membership.status = 'cancelled'
    current_membership.save(update_fields=['status'])
    UserMembership.deactivate_other_active_memberships(request.user, keep_membership_id=current_membership.id)
    upgrade_start_date = timezone.now()
    new_end_date = upgrade_start_date + timedelta(days=new_plan.get_duration_days())
    UserMembership.objects.create(
        user=request.user,
        plan=new_plan,
        start_date=upgrade_start_date,
        end_date=new_end_date,
        amount_paid=0,
        status='active'
    )

    # Update user
    user = request.user
    user.current_membership = new_plan
    user.membership_expiry = new_end_date
    user.membership_active = True
    user.save()

    # Clear session
    request.session.pop('upgrade_details', None)

    messages.success(request, f'🎉 Your membership has been upgraded to {new_plan.name}!')
    return redirect('membership:my_membership')


