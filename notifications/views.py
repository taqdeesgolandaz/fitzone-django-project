from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Notification, NewsletterSubscriber
from .services import NotificationService
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone


@staff_member_required
def admin_notifications(request):
    """Admin-facing notifications listing (fallback for /admin/notifications/)"""
    # Clear any existing Django flash messages so they don't show up on this admin page
    try:
        storage = messages.get_messages(request)
        # Mark as used to prevent display
        storage.used = True
    except Exception:
        pass
    # Show notifications created for staff, most recent first
    notifications_qs = Notification.objects.filter(user__is_staff=True).order_by('-created_at')

    # Optional filtering by type
    current_type = request.GET.get('type')
    if current_type:
        notifications_qs = notifications_qs.filter(notification_type=current_type)

    # Counts
    unread_count = notifications_qs.filter(is_read=False).count()
    today = timezone.now().date()
    today_count = notifications_qs.filter(created_at__date=today).count()

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications_qs, 20)
    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
        'today_count': today_count,
        'current_type': current_type,
    }
    return render(request, 'notifications/admin_notifications.html', context)


@staff_member_required
def admin_open_notification(request, notification_id):
    """Mark notification as read and redirect to its link (if present)"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.mark_as_read()
    target = notification.link or reverse('notifications:list')
    return redirect(target)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@login_required
def notification_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    if request.GET.get('mark_all_read'):
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')


@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """API endpoint to get unread notification count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


def subscribe_newsletter(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        next_url = request.POST.get('next', '/')  # Get the redirect URL
        
        if not email:
            messages.error(request, 'Email is required.')
            return redirect(next_url)

        # Normalize and validate email format
        email = email.strip()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(next_url)
        
        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.warning(request, 'This email is already subscribed.')
            return redirect(next_url)
        
        try:
            NewsletterSubscriber.objects.create(email=email)
            # Notify admin/staff about new subscriber
            NotificationService.create_staff_notification(
                title="New Newsletter Subscriber",
                message=f"New subscriber: {email}",
                notification_type='system',
                link=reverse('notifications:newsletter_subscribers')
            )
            messages.success(request, 'Successfully subscribed to newsletter!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect(next_url)
    
    return redirect('/')


@staff_member_required
def newsletter_subscribers(request):
    """View all newsletter subscribers (admin only)"""
    subscribers = NewsletterSubscriber.objects.all()
    total = subscribers.count()
    active = subscribers.filter(is_active=True).count()
    
    context = {
        'subscribers': subscribers,
        'total': total,
        'active': active,
    }
    return render(request, 'admin_dashboard/newsletter.html', context)


@staff_member_required
def export_subscribers(request):
    """Export subscribers as CSV"""
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Subscribed Date', 'Status'])
    
    subscribers = NewsletterSubscriber.objects.all()
    for sub in subscribers:
        writer.writerow([sub.email, sub.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'), 'Active' if sub.is_active else 'Inactive'])
    
    return response


@staff_member_required
def delete_subscriber(request, subscriber_id):
    """Delete a subscriber"""
    subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
    email = subscriber.email
    subscriber.delete()
    messages.success(request, f'Subscriber {email} has been deleted.')
    return redirect('notifications:newsletter_subscribers')