from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Trainer, TrainerSession, TrainerReview
from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from notifications.services import NotificationService
from django.urls import reverse


def trainer_list(request):
    """Display all available trainers"""
    trainers = Trainer.objects.filter(is_available=True, is_verified=True)
    
    # Filter by specialization
    specialization = request.GET.get('specialization')
    if specialization:
        trainers = trainers.filter(specialization=specialization)
    
    # Search by name
    search = request.GET.get('search')
    if search:
        trainers = trainers.filter(
            Q(full_name__icontains=search) |
            Q(bio__icontains=search)
        )
    
    context = {
        'trainers': trainers,
        'specializations': Trainer.SPECIALIZATIONS,
        'selected_specialization': specialization,
        'search_query': search,
    }
    return render(request, 'trainers/list.html', context)


def trainer_detail(request, trainer_id):
    """Display trainer details and booking form"""
    trainer = get_object_or_404(Trainer, id=trainer_id, is_available=True, is_verified=True)
    reviews = trainer.reviews.all()[:10]
    
    # Generate available time slots (simplified)
    available_slots = generate_available_slots(trainer)
    
    context = {
        'trainer': trainer,
        'reviews': reviews,
        'available_slots': available_slots,
    }
    return render(request, 'trainers/detail.html', context)


@login_required
def book_session(request, trainer_id):
    """Book a session with a trainer"""
    trainer = get_object_or_404(Trainer, id=trainer_id, is_available=True, is_verified=True)
    
    if request.method == 'POST':
        session_date = request.POST.get('session_date')
        session_time = request.POST.get('session_time')
        session_type = request.POST.get('session_type', 'online')
        user_notes = request.POST.get('user_notes', '')
        
        # Create session
        # This trainer booking form is for the monthly subscription plan
        amount_to_charge = trainer.monthly_rate

        session = TrainerSession.objects.create(
            user=request.user,
            trainer=trainer,
            session_type=session_type,
            session_date=session_date,
            session_time=session_time,
            duration_minutes=60,
            amount=amount_to_charge,
            user_notes=user_notes,
            status='pending'
        )
        
        # Notify staff/admin about new booking request
        NotificationService.create_staff_notification(
            title="New Trainer Booking",
            message=f"{request.user.get_full_name() or request.user.username} requested a session with {trainer.full_name} on {session_date}",
            notification_type='trainer',
            link=reverse('trainers:admin_bookings')
        )

        messages.success(request, f'Booking request sent to {trainer.full_name}! They will confirm soon.')
        return redirect('trainers:my_sessions')
    
    return redirect('trainers:detail', trainer_id=trainer_id)


@login_required
def my_sessions(request):
    """View user's booked sessions"""
    from django.utils import timezone
    import datetime
    
    current_date = timezone.now().date()
    
    upcoming_sessions = TrainerSession.objects.filter(
        user=request.user,
        session_date__gte=current_date,
        status__in=['pending', 'approved']
    ).order_by('session_date', 'session_time')
    
    past_sessions = TrainerSession.objects.filter(
        user=request.user,
        session_date__lt=current_date,
        status__in=['completed', 'rejected', 'cancelled']
    ).order_by('-session_date')
    
    completed_sessions = TrainerSession.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-session_date')[:10]
    
    rejected_sessions = TrainerSession.objects.filter(
        user=request.user,
        status='rejected'
    ).order_by('-session_date')[:10]
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'completed_sessions': completed_sessions,
        'rejected_sessions': rejected_sessions,
    }
    return render(request, 'trainers/my_sessions.html', context)

@login_required
def session_detail(request, session_id):
    """Display trainer session details and payment actions"""
    session = get_object_or_404(TrainerSession, id=session_id, user=request.user)
    context = {
        'session': session,
    }
    return render(request, 'trainers/session_detail.html', context)

@login_required
def cancel_session(request, session_id):
    """Cancel a booked session"""
    session = get_object_or_404(TrainerSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        session.status = 'cancelled'
        session.cancellation_reason = cancellation_reason
        session.save()
        
        # Send notification to user
        from notifications.services import NotificationService
        NotificationService.create_notification(
            user=request.user,
            title="📅 Session Cancelled",
            message=f"Your session with {session.trainer.full_name} on {session.session_date} has been cancelled.",
            notification_type='trainer',
            link='/trainers/my-sessions/'
        )
        
        messages.info(request, 'Session cancelled successfully.')
        return redirect('trainers:my_sessions')
    
    return render(request, 'trainers/cancel_session.html', {'session': session})


@staff_member_required
def admin_bookings(request):
    """Admin view to manage all trainer bookings"""
    pending_bookings = TrainerSession.objects.filter(status='pending').order_by('session_date', 'session_time')
    approved_bookings = TrainerSession.objects.filter(status='approved').order_by('-session_date')
    completed_bookings = TrainerSession.objects.filter(status='completed').order_by('-session_date')[:20]
    rejected_bookings = TrainerSession.objects.filter(status='rejected').order_by('-session_date')[:20]
    
    stats = {
        'total_pending': pending_bookings.count(),
        'total_approved': approved_bookings.count(),
        'total_completed': completed_bookings.count(),
        'total_rejected': rejected_bookings.count(),
    }
    
    context = {
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'completed_bookings': completed_bookings,
        'rejected_bookings': rejected_bookings,
        'stats': stats,
    }
    return render(request, 'trainers/admin_bookings.html', context)

@staff_member_required
def approve_booking(request, booking_id):
    """Admin approve a booking"""
    booking = get_object_or_404(TrainerSession, id=booking_id)
    booking.status = 'approved'
    booking.save()
    
    if booking.session_type == 'online' and not booking.meeting_link:
        booking.meeting_link = f"https://meet.google.com/new"
        booking.save()
    
    from notifications.services import NotificationService
    NotificationService.create_notification(
        user=booking.user,
        title="✅ Booking Approved!",
        message=f"Your session with {booking.trainer.full_name} on {booking.session_date} at {booking.session_time} has been approved.",
        notification_type='trainer',
        link=reverse('trainers:session_detail', args=[booking.id])
    )
    
    messages.success(request, f'Booking for {booking.user.username} has been approved!')
    return redirect('trainers:admin_bookings')


@staff_member_required
def reject_booking(request, booking_id):
    """Admin reject a booking"""
    booking = get_object_or_404(TrainerSession, id=booking_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        booking.status = 'rejected'
        booking.cancellation_reason = rejection_reason
        booking.save()
        
        # Send notification to user - UPDATED LINK
        from notifications.services import NotificationService
        NotificationService.create_notification(
            user=booking.user,
            title="❌ Booking Rejected",
            message=f"Your session request with {booking.trainer.full_name} on {booking.session_date} has been rejected. Reason: {rejection_reason or 'Not specified'}",
            notification_type='trainer',
            link=reverse('trainers:my_sessions') + '#rejected'
        )
        
        messages.info(request, f'Booking for {booking.user.username} has been rejected.')
        return redirect('trainers:admin_bookings')
    
    return render(request, 'trainers/reject_booking.html', {'booking': booking})


@staff_member_required
def mark_completed(request, booking_id):
    """Admin mark a booking as completed"""
    booking = get_object_or_404(TrainerSession, id=booking_id)
    booking.status = 'completed'
    booking.save()
    
    # Send notification to user
    from notifications.services import NotificationService
    NotificationService.create_notification(
        user=booking.user,
        title="🎉 Session Completed!",
        message=f"Your session with {booking.trainer.full_name} has been completed. Please leave a review!",
        notification_type='trainer',
        link=reverse('trainers:add_review', args=[booking.trainer.id])
    )
    
    messages.success(request, f'Booking for {booking.user.username} marked as completed!')
    return redirect('trainers:admin_bookings')   


@login_required
def add_review(request, trainer_id):
    """Add review for a trainer"""
    trainer = get_object_or_404(Trainer, id=trainer_id)
    
    # Check if user has completed a session with this trainer
    has_completed_session = TrainerSession.objects.filter(
        user=request.user,
        trainer=trainer,
        status='completed'
    ).exists()
    
    if not has_completed_session:
        messages.error(request, 'You can only review trainers you have had a session with.')
        return redirect('trainers:detail', trainer_id=trainer_id)
    
    # Check if already reviewed
    existing_review = TrainerReview.objects.filter(user=request.user, trainer=trainer).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this trainer.')
        return redirect('trainers:detail', trainer_id=trainer_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review', '')
        
        review = TrainerReview.objects.create(
            user=request.user,
            trainer=trainer,
            rating=rating,
            review=review_text
        )
        
        # Update trainer rating
        reviews = trainer.reviews.all()
        total_rating = sum(r.rating for r in reviews)
        trainer.average_rating = total_rating / reviews.count()
        trainer.total_ratings = reviews.count()
        trainer.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('trainers:detail', trainer_id=trainer_id)
    
    return render(request, 'trainers/add_review.html', {'trainer': trainer})


def generate_available_slots(trainer):
    """Generate available time slots for a trainer"""
    # Simplified - returns common time slots
    time_slots = [
        '09:00', '10:00', '11:00', '12:00', '13:00', 
        '14:00', '15:00', '16:00', '17:00', '18:00'
    ]
    
    # Get next 7 days
    dates = []
    for i in range(7):
        date = timezone.now().date() + timedelta(days=i)
        dates.append({
            'date': date,
            'date_str': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'slots': time_slots
        })
    
    return dates