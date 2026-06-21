from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import SupportMessage
from notifications.services import NotificationService
from django.urls import reverse

def contact_view(request):
    """Contact Us page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        phone = request.POST.get('phone', '')
        
        if not name or not email or not subject or not message:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'support/contact.html')
        
        try:
            support_msg = SupportMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                message_type='contact',
                subject=subject,
                message=message
            )
            
            # Store in session for success page
            request.session['form_success'] = True
            request.session['form_message'] = 'Your message has been sent successfully!'
            
            # Notify staff/admin
            NotificationService.create_staff_notification(
                title="New Contact Message",
                message=f"Contact from {name} <{email}>: {subject}",
                notification_type='system',
                link=reverse('support:admin_messages')
            )

            # Redirect to success page
            return redirect('support:success')
            
        except Exception as e:
            messages.error(request, f'An error occurred. Please try again.')
            return render(request, 'support/contact.html')
    
    return render(request, 'support/contact.html')


def contact_support_view(request):
    """Contact Support page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        phone = request.POST.get('phone', '')
        
        if not name or not email or not subject or not message:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'support/contact_support.html')
        
        try:
            support_msg = SupportMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                message_type='support',
                category=category,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your support request has been submitted! We will respond within 24 hours.')

            # Notify staff/admin
            NotificationService.create_staff_notification(
                title="New Support Request",
                message=f"Support request from {name} <{email}>: {subject}",
                notification_type='system',
                link=reverse('support:admin_messages')
            )
            return redirect('support:contact_support')
        except Exception as e:
            messages.error(request, f'An error occurred. Please try again.')
            return render(request, 'support/contact_support.html')
    
    return render(request, 'support/contact_support.html')


def report_problem_view(request):
    """Report a Problem page"""
    
    # Clear all existing messages when visiting this page
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        print("="*50)
        print("REPORT PROBLEM SUBMITTED")
        print("="*50)
        
        name = request.POST.get('name', 'Anonymous')
        email = request.POST.get('email')
        problem_type = request.POST.get('problem_type')
        description = request.POST.get('description')
        steps = request.POST.get('steps', '')
        urgency = request.POST.get('urgency', 'medium')
        device = request.POST.get('device', '')
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Problem Type: {problem_type}")
        print(f"Description: {description[:50] if description else 'None'}...")
        
        # Validation
        if not email or not description:
            print("VALIDATION FAILED - Missing email or description")
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'support/report_problem.html')
        
        try:
            support_msg = SupportMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                message_type='report',
                problem_type=problem_type,
                subject=f"Problem Report: {problem_type}",
                message=description,
                steps_to_reproduce=steps,
                urgency=urgency,
                device_info=device,
            )
            print(f"✅ Report saved! ID: {support_msg.id}")
            
            # Store in session
            request.session['report_success'] = True
            request.session['report_id'] = support_msg.id
            
            messages.success(request, 'Your problem report has been submitted successfully!')
            # Notify staff/admin
            NotificationService.create_staff_notification(
                title="New Problem Report",
                message=f"Problem report from {name} <{email}>: {problem_type}",
                notification_type='system',
                link=reverse('support:admin_messages')
            )
            return redirect('support:report_success')
            
        except Exception as e:
            print(f"❌ Error: {e}")
            messages.error(request, f'An error occurred. Please try again.')
            return render(request, 'support/report_problem.html')
    
    return render(request, 'support/report_problem.html')


def report_success_view(request):
    """Success page after reporting a problem"""
    report_id = request.session.get('report_id')
    
    if not report_id:
        return redirect('support:report_problem')
    
    # Clear session
    request.session['report_success'] = False
    request.session['report_id'] = None
    
    context = {
        'report_id': report_id,
    }
    return render(request, 'support/report_success.html', context)


def faq_view(request):
    """FAQ page"""
    faqs = [
        {
            'question': 'What is FitZone?',
            'answer': 'FitZone is a comprehensive fitness platform that provides personalized workout plans, diet guidance, professional trainers, and progress tracking.',
            'category': 'General'
        },
        {
            'question': 'How do I get started?',
            'answer': 'Simply create an account, choose a membership plan that suits your needs, and start exploring our workout and diet plans.',
            'category': 'Getting Started'
        },
        {
            'question': 'How do I contact support?',
            'answer': 'You can contact us through the Contact Support page, email us at support@fitzone.com, or call us at +91 98765 43210.',
            'category': 'Support'
        },
    ]
    return render(request, 'support/faq.html', {'faqs': faqs})


def privacy_policy_view(request):
    """Privacy Policy page"""
    return render(request, 'support/privacy_policy.html')


def terms_of_service_view(request):
    """Terms of Service page"""
    return render(request, 'support/terms_of_service.html')


def refund_policy_view(request):
    """Refund Policy page"""
    return render(request, 'support/refund_policy.html')


def success_view(request):
    """Success page for contact/support forms"""
    if not request.session.get('form_success'):
        return redirect('support:contact')
    
    request.session['form_success'] = False
    return render(request, 'support/success.html')


def error_view(request, error_message=None):
    """Error page for form submission"""
    context = {
        'error_message': error_message or 'Something went wrong. Please try again.'
    }
    return render(request, 'support/error.html', context)


@staff_member_required
def admin_messages_view(request):
    """Admin view to see all support messages"""
    messages_list = SupportMessage.objects.all()
    
    # Filter by type
    message_type = request.GET.get('type')
    if message_type:
        messages_list = messages_list.filter(message_type=message_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        messages_list = messages_list.filter(status=status)
    
    stats = {
        'total': SupportMessage.objects.count(),
        'pending': SupportMessage.objects.filter(status='pending').count(),
        'contact': SupportMessage.objects.filter(message_type='contact').count(),
        'support': SupportMessage.objects.filter(message_type='support').count(),
        'report': SupportMessage.objects.filter(message_type='report').count(),
    }
    
    context = {
        'support_messages': messages_list,
        'stats': stats,
        'current_type': message_type,
        'current_status': status,
    }
    return render(request, 'support/admin_messages.html', context)


@staff_member_required
def admin_message_detail(request, message_id):
    """Admin view to see message details and reply"""
    message = get_object_or_404(SupportMessage, id=message_id)
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes')
        status = request.POST.get('status')
        
        message.admin_notes = admin_notes
        message.status = status
        if status == 'resolved':
            message.resolved_at = timezone.now()
        message.save()
        
        messages.success(request, 'Message updated successfully!')
        return redirect('support:admin_message_detail', message_id=message.id)
    
    # Mark as read when viewed
    if message.status == 'pending':
        message.status = 'read'
        message.save()
    
    return render(request, 'support/admin_message_detail.html', {'message': message})


@staff_member_required
def admin_message_delete(request, message_id):
    """Delete a support message"""
    message = get_object_or_404(SupportMessage, id=message_id)
    message.delete()
    messages.success(request, 'Message deleted successfully!')
    return redirect('support:admin_messages')