import json
import re
import uuid
from urllib.parse import quote
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
except Exception:
    razorpay_client = None
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


@login_required
def check_payment_status(request, transaction_id):
    """Check if payment has been confirmed."""
    payment = Payment.objects.filter(
        user=request.user,
        transaction_id=transaction_id
    ).first()

    if payment and payment.status == 'success':
        return JsonResponse({'status': 'completed'})
    elif payment and payment.status == 'failed':
        return JsonResponse({'status': 'failed'})
    else:
        return JsonResponse({'status': 'pending'})


@csrf_exempt
def upi_payment_webhook(request):
    """Webhook to confirm UPI payments automatically."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        amount = data.get('amount')
        reference_id = data.get('reference_id')

        if not transaction_id:
            return JsonResponse({'status': 'error', 'message': 'Transaction ID required'}, status=400)

        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)

        if status == 'success':
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.transaction_id = reference_id or transaction_id
            payment.save()

            # Activate membership
            plan = payment.plan or MembershipPlan.objects.filter(id=payment.plan_id).first()
            if plan:
                end_date = timezone.now() + timedelta(days=plan.get_duration_days())
                membership, created = UserMembership.objects.get_or_create(
                    user=payment.user,
                    plan=plan,
                    defaults={
                        'end_date': end_date,
                        'amount_paid': payment.amount,
                        'status': 'active',
                        'payment_id': payment.transaction_id
                    }
                )
                if not created:
                    membership.end_date = end_date
                    membership.status = 'active'
                    membership.amount_paid = payment.amount
                    membership.save()

                # Update user
                user = payment.user
                user.current_membership = plan
                user.membership_expiry = end_date
                user.membership_active = True
                user.save()

        elif status == 'failed':
            payment.status = 'failed'
            payment.save()

        return JsonResponse({
            'status': 'success',
            'payment_id': payment.id,
            'payment_status': payment.status
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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
        if razorpay_client is None:
            raise RuntimeError('Razorpay client is unavailable. Please install the Razorpay SDK or check configuration.')

        razorpay_order = razorpay_client.order.create(data=order_data)
        
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
def create_session_order(request, session_id):
    """Create a Razorpay order for a trainer session via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    if razorpay_client is None:
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
        order = razorpay_client.order.create(data=order_data)
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
def payment_history(request):
    if active_membership:
        messages.warning(request, 'You already have an active membership.')
        return redirect('membership:my_membership')

