from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from notifications.services import NotificationService, send_email_via_brevo
from notifications.email_templates import get_password_reset_email
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import translation
import sys
import time
import smtplib
import ssl
import traceback
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from urllib3 import request
from threading import Thread
from .models import CustomUser
from .forms import UserProfileForm, UserSettingsForm
from .serializers import (UserSerializer, RegisterSerializer, 
                         UserProfileSerializer, ChangePasswordSerializer)
from .signals import ensure_single_session

User = get_user_model()


def send_email_async(subject, message, from_email, recipient_list, html_message=None):
    """Send email in background thread without letting failures crash the request."""
    def send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Async email error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    thread = Thread(target=send, daemon=True)
    thread.start()


def send_email_sync(subject, message, from_email, recipient_list, html_message=None, email_type='generic'):
    """Send email synchronously and return False on failure."""
    try:
        if getattr(settings, 'BREVO_API_KEY', ''):
            brevo_result = send_email_via_brevo(
                subject=subject,
                plain_content=message,
                html_content=html_message,
                from_email=from_email,
                recipient_list=recipient_list,
            )
            if brevo_result is True:
                return True
            print(f"[send_email_sync] Brevo API result={brevo_result}", file=sys.stderr)
            return False

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Sync email error ({email_type}): {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

# Import for achievements
from achievements.models import UserAchievement, Badge

# ==================== TEMPLATE VIEWS (for web browser) ====================

def home_view(request):
    """Landing page view"""
    from membership.models import MembershipPlan
    
    # Get active membership plans for home page
    plans = MembershipPlan.objects.filter(is_active=True).order_by('price')
    
    context = {
        'plans': plans,
    }
    return render(request, 'base/home.html', context)

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """Render login page and handle login"""
    
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard:dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Debug: log incoming cookies and CSRF token to help diagnose mobile POSTs
        try:
            print(f"[login_view] POST remote_addr={request.META.get('REMOTE_ADDR')} cookies={request.COOKIES}", file=sys.stderr)
            print(f"[login_view] POST csrfmiddlewaretoken={request.POST.get('csrfmiddlewaretoken')} x-csrftoken={request.META.get('HTTP_X_CSRFTOKEN')}", file=sys.stderr)
            print(f"[login_view] POST headers origin={request.META.get('HTTP_ORIGIN')} referer={request.META.get('HTTP_REFERER')} host={request.META.get('HTTP_HOST')}", file=sys.stderr)
        except Exception:
            pass

        username_or_email = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        print(f"[login_view] POST credentials username_or_email={username_or_email!r} password_length={len(password)}", file=sys.stderr)

        # Local fallback: if token is provided and cookie is missing, trust POST token in DEBUG
        if settings.DEBUG and 'csrftoken' not in request.COOKIES:
            post_token = (
                request.POST.get('csrfmiddlewaretoken') or
                request.POST.get(settings.CSRF_COOKIE_NAME) or
                request.META.get('HTTP_X_CSRFTOKEN')
            )
            if post_token:
                request.COOKIES[settings.CSRF_COOKIE_NAME] = post_token
                print(f"[login_view] injected csrftoken from POST in DEBUG mode token={post_token}", file=sys.stderr)

        username = username_or_email
        if '@' in username_or_email:
            try:
                user_obj = CustomUser.objects.get(email__iexact=username_or_email)
                username = user_obj.username
            except CustomUser.DoesNotExist:
                username = username_or_email

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['login_confirmed'] = True
            request.session.save()
            messages.success(request, 'Login successful!')
            print(f"[login_view] authenticated user={user.username} session_key={request.session.session_key}", file=sys.stderr)

            redirect_to = 'admin_dashboard:dashboard' if user.is_staff else 'dashboard'
            response = redirect(redirect_to)
            if settings.DEBUG:
                session_key = request.session.session_key
                max_age = settings.SESSION_COOKIE_AGE

                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    session_key,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=None,
                    max_age=max_age,
                )

                csrf_token = request.COOKIES.get(settings.CSRF_COOKIE_NAME) or request.POST.get('csrfmiddlewaretoken') or get_token(request)
                response.set_cookie(
                    settings.CSRF_COOKIE_NAME,
                    csrf_token,
                    secure=settings.CSRF_COOKIE_SECURE,
                    httponly=settings.CSRF_COOKIE_HTTPONLY,
                    samesite=settings.CSRF_COOKIE_SAMESITE,
                    path=settings.CSRF_COOKIE_PATH,
                    domain=None,
                    max_age=max_age,
                )
                print(
                    f"[login_view] ✅ Cookies set on login response: session_key={session_key} max_age={max_age}",
                    file=sys.stderr,
                )
            return response
        else:
            print(f"[login_view] authentication failed for username={username!r}", file=sys.stderr)
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'accounts/login.html')
    
    # Clear only old/expired messages for GET requests
    storage = messages.get_messages(request)
    storage.used = True

    response = render(request, 'accounts/login.html')
    if settings.DEBUG:
        token = get_token(request)
        response.set_cookie(
            settings.CSRF_COOKIE_NAME,
            token,
            secure=settings.CSRF_COOKIE_SECURE,
            httponly=settings.CSRF_COOKIE_HTTPONLY,
            samesite=settings.CSRF_COOKIE_SAMESITE,
            path=settings.CSRF_COOKIE_PATH,
            domain=None,
            max_age=settings.CSRF_COOKIE_AGE,
        )
        print(
            f"[login_view] GET set csrftoken cookie host={request.get_host()} "
            f"CSRF_DOMAIN={settings.CSRF_COOKIE_DOMAIN} token={token} max_age={settings.CSRF_COOKIE_AGE}",
            file=sys.stderr,
        )
    return response


def get_csrf_token(request):
    """Force-set a CSRF cookie and return the token for mobile diagnostics."""
    token = get_token(request)
    response = JsonResponse({'csrf_token': token})
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        token,
        secure=settings.CSRF_COOKIE_SECURE,
        httponly=settings.CSRF_COOKIE_HTTPONLY,
        samesite=settings.CSRF_COOKIE_SAMESITE,
        path=settings.CSRF_COOKIE_PATH,
        domain=None,
        max_age=getattr(settings, 'CSRF_COOKIE_AGE', 1209600),
    )
    print(f"[get_csrf_token] CSRF cookie forced set: {token}", file=sys.stderr)
    return response


def register_view(request):
    """Render registration page and handle registration"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard:dashboard')
        return redirect('dashboard')
    
    context = {}
    
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.POST)
        
        if serializer.is_valid():
            user = serializer.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to FitZone!')
            return redirect('dashboard')
        else:
            # Collect unique, user-friendly error messages and pass to template (do NOT add to messages())
            seen_errors = []
            for field, errors in serializer.errors.items():
                pretty_field = field.replace('_', ' ').title() if field != 'non_field_errors' else ''
                for error in errors:
                    # Suppress the mobile-number 'required' message from the form error box
                    if field == 'mobile_number' and str(error).strip().lower() in (
                        'mobile number is required.',
                        'this field may not be blank.'
                    ):
                        continue
                    msg = f"{pretty_field + ': ' if pretty_field else ''}{error}"
                    if msg not in seen_errors:
                        seen_errors.append(msg)
            context['form_errors'] = seen_errors

            # Store form data for pre-filling the form, but exclude passwords for security
            form_data = request.POST.copy()
            form_data.pop('password', None)
            form_data.pop('password2', None)
            context['form_data'] = form_data
    
    return render(request, 'accounts/register.html', context)


def forgot_password(request):
    """Forgot password page"""
    if request.method == 'POST':
        print(f"[forgot_password] POST received at {time.time()}")
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/forgot_password.html')
        
        try:
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                messages.error(request, 'No account found with this email address.')
                return render(request, 'accounts/forgot_password.html')

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Always use SITE_URL from settings for reset link (not request.build_absolute_uri)
            site_url = getattr(settings, 'SITE_URL', None) or 'http://localhost:8000'
            site = site_url.rstrip('/')
            reset_link = f"{site}{reverse('reset_password', kwargs={'uidb64': uid, 'token': token})}"
            
            subject = '[FitZone] Password Reset Request'
            html_content, plain_content = get_password_reset_email(user, reset_link)

            print(f"[forgot_password] starting send at {time.time()}")
            print(
                f"[forgot_password] email settings BACKEND={settings.EMAIL_BACKEND} HOST={settings.EMAIL_HOST} PORT={settings.EMAIL_PORT} TLS={settings.EMAIL_USE_TLS} SSL={settings.EMAIL_USE_SSL} USER_SET={bool(settings.EMAIL_HOST_USER)} PASSWORD_SET={bool(settings.EMAIL_HOST_PASSWORD)} BREVO_API_KEY_SET={bool(getattr(settings, 'BREVO_API_KEY', ''))}"
            )

            # If Brevo API key is configured, use API (avoids Render blocking SMTP on port 587).
            if getattr(settings, 'BREVO_API_KEY', ''):
                print(f"[forgot_password] attempting Brevo API send at {time.time()}", file=sys.stderr)
                brevo_result = send_email_via_brevo(
                    subject=subject,
                    plain_content=plain_content,
                    html_content=html_content,
                    from_email=getattr(settings, 'BREVO_SENDER_EMAIL', settings.DEFAULT_FROM_EMAIL),
                    recipient_list=[user.email],
                )
                print(f"[forgot_password] brevo_result={brevo_result} at {time.time()}", file=sys.stderr)
                if not brevo_result:
                    messages.error(request, 'Unable to send password reset email right now. Please try again later.')
                    return render(request, 'accounts/forgot_password.html')
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')

            # Fallback to SMTP-based sender (may timeout on Render)
            email_sent = send_email_sync(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                email_type='password_reset',
            )
            print(f"[forgot_password] send result={email_sent} at {time.time()}")
            if not email_sent:
                messages.error(request, 'Unable to send password reset email right now. Please try again later.')
                return render(request, 'accounts/forgot_password.html')
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        except Exception as e:
            print(f"[forgot_password] unhandled exception: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            messages.error(request, 'An unexpected error occurred. Please try again or contact support.')
            return render(request, 'accounts/forgot_password.html')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, uidb64, token):
    """Reset password page"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or not confirm_password:
                messages.error(request, 'Please fill in both password fields.')
                return render(request, 'accounts/reset_password.html', {'valid': True})

            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'accounts/reset_password.html', {'valid': True})

            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
                return render(request, 'accounts/reset_password.html', {'valid': True})

            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
            return redirect('login')

        return render(request, 'accounts/reset_password.html', {'valid': True})

    messages.error(request, 'The password reset link is invalid or has expired. Please request a new one.')
    return render(request, 'accounts/forgot_password.html')

@login_required
def dashboard_view(request):
    """User dashboard view with real data - No membership required"""
    from workouts.models import UserWorkoutProgress, WorkoutPlan
    from tracking.models import FitnessProgress

    # Get achievements count for badge
    earned_badge_ids = UserAchievement.objects.filter(user=request.user).values_list('badge_id', flat=True)
    available_badges_count = Badge.objects.filter(is_active=True).exclude(id__in=earned_badge_ids).count()

    # Get BMI (works even without membership)
    bmi = request.user.calculate_bmi()
    bmi_category = request.user.get_bmi_category()

    # Get today's workout (visible but may redirect if no membership when clicked)
    today = timezone.now().date()
    weekday = today.strftime('%A').lower()
    today_workout = WorkoutPlan.objects.filter(day_of_week=weekday, is_active=True).first()

    # Get weight chart data (works even without membership)
    weight_records = FitnessProgress.objects.filter(user=request.user).order_by('date_recorded')[:10]
    weight_chart_data = {
        'dates': [r.date_recorded.strftime('%b %d') for r in weight_records],
        'weights': [r.weight for r in weight_records],
    }

    # Get workout statistics (works even without membership)
    workout_logs = UserWorkoutProgress.objects.filter(user=request.user)
    this_month = timezone.now().month
    completed_workouts = workout_logs.filter(status='completed')
    workout_stats = {
        'total_workouts': completed_workouts.count(),
        'this_month': completed_workouts.filter(scheduled_date__month=this_month).count(),
        'total_calories': sum(w.calories_burned for w in completed_workouts),
        'streak': calculate_streak(workout_logs),
        'completion_rate': int((completed_workouts.count() / max(workout_logs.count(), 1)) * 100),
    }

    # Get recent workouts
    recent_workouts = workout_logs.order_by('-scheduled_date')[:5]

    # Recent activities
    recent_activities = []
    for w in recent_workouts:
        recent_activities.append({
            'title': f'Completed {w.workout_plan.name}',
            'icon': 'fa-dumbbell',
            'time': w.completed_date or w.created_at,
        })

    context = {
        'user': request.user,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'today_workout': today_workout,
        'weight_chart_data': weight_chart_data,
        'workout_stats': workout_stats,
        'recent_workouts': recent_workouts,
        'recent_activities': recent_activities[:5],
        'available_badges_count': available_badges_count,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


def calculate_streak(workout_logs):
    """Calculate current workout streak"""
    streak = 0
    completed_dates = set(workout_logs.filter(status='completed').values_list('scheduled_date', flat=True))
    current_date = timezone.now().date()

    while current_date in completed_dates:
        streak += 1
        current_date -= timezone.timedelta(days=1)

    return streak

@login_required
def logout_view(request):
    """Logout user"""
    # Clear all existing messages first
    storage = messages.get_messages(request)
    storage.used = True
    
    # Logout the user
    logout(request)
    
    # Add fresh logout message
    messages.success(request, 'You have been successfully logged out!')
    
    return redirect('login')

# ==================== API VIEWS (for mobile apps) ====================

class RegisterView(generics.CreateAPIView):
    """User Registration View"""
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """User Login View"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'error': 'Please provide both username/email and password'},
                          status=status.HTTP_400_BAD_REQUEST)

        username = username_or_email
        if '@' in username_or_email:
            try:
                user_obj = CustomUser.objects.get(email__iexact=username_or_email)
                username = user_obj.username
            except CustomUser.DoesNotExist:
                username = username_or_email

        user = authenticate(request, username=username, password=password)
        
        if user:
            ensure_single_session(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful!'
            })
        else:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """User Logout View (Blacklists refresh token)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and Update User Profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ChangePasswordView(APIView):
    """Change User Password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not check_password(serializer.data['old_password'], user.password):
                return Response({'old_password': 'Wrong password.'},
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully!'},
                          status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    """Get User Details by ID"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@login_required
def profile_view(request):
    """User profile page - view and edit profile"""
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'bmi': request.user.calculate_bmi(),
        'bmi_category': request.user.get_bmi_category(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Change user password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('login')

    return redirect('settings')


@login_required
def settings_view(request):
    """User settings page"""
    from payments.models import Payment
    from workouts.models import UserWorkoutProgress
    from trainers.models import TrainerSession
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)

    recent_payments = list(
        Payment.objects.filter(user=request.user)
        .order_by('-created_at')
        .values('invoice_number', 'amount', 'status', 'payment_method', 'created_at', 'paid_at')[:10]
    )
    recent_workouts = list(
        UserWorkoutProgress.objects.filter(user=request.user)
        .select_related('workout_plan')
        .order_by('-scheduled_date')
        .values('scheduled_date', 'completed_date', 'status', 'calories_burned', 'duration_minutes', 'workout_plan__name')[:10]
    )
    recent_sessions = list(
        TrainerSession.objects.filter(user=request.user)
        .select_related('trainer')
        .order_by('-session_date', '-session_time')
        .values('session_date', 'session_time', 'status', 'session_type', 'amount', 'trainer__full_name')[:10]
    )

    # Connected accounts UI removed — no social provider context passed
    
    return render(request, 'accounts/settings.html', {
        'form': form,
        'recent_payments': recent_payments,
        'recent_workouts': recent_workouts,
        'recent_sessions': recent_sessions,
        # social account context intentionally omitted
        'user_agent': request.META.get('HTTP_USER_AGENT', 'This browser'),
    })


def set_language(request):
    """Set the current language for the session and optionally persist on user profile."""
    from django.conf import settings
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    lang = request.POST.get('language')
    if lang and lang in dict(getattr(settings, 'LANGUAGES', [])):
        # Use the configured language cookie name for session storage
        session_key = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
        request.session[session_key] = lang
        translation.activate(lang)
        if getattr(request, 'user', None) and request.user.is_authenticated:
            try:
                request.user.language = lang
                request.user.save(update_fields=['language'])
            except Exception:
                pass
    return redirect(next_url)


@login_required
def delete_account(request):
    """Delete user account"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    
    return render(request, 'accounts/delete_account.html')





def faq_view(request):
    """FAQ page"""
    faqs = [
        {
            'question': 'What is FitZone?',
            'answer': 'FitZone is a comprehensive fitness platform that provides personalized workout plans, diet guidance, professional trainers, and progress tracking to help you achieve your fitness goals.',
            'category': 'General'
        },
        {
            'question': 'How do I get started?',
            'answer': 'Simply create an account, choose a membership plan that suits your needs, and start exploring our workout and diet plans. You can also book sessions with our expert trainers.',
            'category': 'Getting Started'
        },
        {
            'question': 'Do I need any equipment?',
            'answer': 'Many of our workouts can be done with just body weight. Some advanced workouts may require basic equipment like dumbbells or resistance bands.',
            'category': 'Workouts'
        },
        {
            'question': 'Can I change my membership plan?',
            'answer': 'Yes, you can upgrade or downgrade your membership plan at any time. The changes will take effect from your next billing cycle.',
            'category': 'Membership'
        },
        {
            'question': 'How do I cancel my membership?',
            'answer': 'You can cancel your membership from your account settings. Your membership will remain active until the end of your current billing period.',
            'category': 'Membership'
        },
        {
            'question': 'Is there a free trial?',
            'answer': 'We offer a 7-day free trial on our Pro and Premium plans. No credit card required to start your trial.',
            'category': 'Membership'
        },
        {
            'question': 'How do I track my progress?',
            'answer': 'Use our tracking dashboard to log your weight, BMI, body measurements, and workout completions. You can view your progress through interactive charts.',
            'category': 'Tracking'
        },
        {
            'question': 'Are the workouts suitable for beginners?',
            'answer': 'Absolutely! We have dedicated beginner workouts that focus on proper form and building foundational strength.',
            'category': 'Workouts'
        },
        {
            'question': 'How do I contact a trainer?',
            'answer': 'You can book a session with any trainer from our trainers page. Once booked, you can communicate with them through the platform.',
            'category': 'Trainers'
        },
        {
            'question': 'Is my payment information secure?',
            'answer': 'Yes, we use Razorpay, a PCI-DSS compliant payment gateway. Your payment information is encrypted and never stored on our servers.',
            'category': 'Payments'
        },
    ]
    return render(request, 'support/faq.html', {'faqs': faqs})


def contact_view(request):
    """Contact Us page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you can add email sending logic
        messages.success(request, 'Thank you for contacting us! We will get back to you within 24 hours.')
        return redirect('contact')
    
    return render(request, 'support/contact.html')


def privacy_policy_view(request):
    """Privacy Policy page"""
    return render(request, 'support/privacy_policy.html')


def terms_of_service_view(request):
    """Terms of Service page"""
    return render(request, 'support/terms_of_service.html')


def refund_policy_view(request):
    """Refund Policy page"""
    return render(request, 'support/refund_policy.html')


def help_center_view(request):
    """Help Center page"""
    topics = [
        {
            'title': 'Getting Started',
            'description': 'Learn how to create an account and set up your profile',
            'icon': 'fas fa-rocket',
            'link': '#',
            'articles': [
                'How to create an account',
                'Setting up your profile',
                'Choosing the right membership plan'
            ]
        },
        {
            'title': 'Membership & Billing',
            'description': 'Manage your subscription and payment methods',
            'icon': 'fas fa-credit-card',
            'link': '#',
            'articles': [
                'How to upgrade your plan',
                'Payment methods accepted',
                'Cancel your membership'
            ]
        },
        {
            'title': 'Workouts & Training',
            'description': 'Get the most out of your workout plans',
            'icon': 'fas fa-dumbbell',
            'link': '#',
            'articles': [
                'How to start a workout',
                'Tracking your progress',
                'Workout tips for beginners'
            ]
        },
        {
            'title': 'Diet & Nutrition',
            'description': 'Personalized diet plans for your goals',
            'icon': 'fas fa-apple-alt',
            'link': '#',
            'articles': [
                'Understanding your diet plan',
                'How to track meals',
                'Nutrition tips'
            ]
        },
        {
            'title': 'Trainers & Sessions',
            'description': 'Book and manage sessions with trainers',
            'icon': 'fas fa-chalkboard-user',
            'link': '#',
            'articles': [
                'How to book a trainer',
                'What to expect from a session',
                'Cancelling a booking'
            ]
        },
        {
            'title': 'Technical Support',
            'description': 'Troubleshooting and technical help',
            'icon': 'fas fa-microchip',
            'link': '#',
            'articles': [
                'App not working?',
                'Payment failed?',
                'Contact technical support'
            ]
        },
    ]
    return render(request, 'support/help_center.html', {'topics': topics})


def contact_support_view(request):
    """Contact Support page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you can add email sending logic
        messages.success(request, 'Your support request has been submitted! We will respond within 24 hours.')
        return redirect('contact_support')
    
    return render(request, 'support/contact_support.html')


def report_problem_view(request):
    """Report a Problem page"""
    if request.method == 'POST':
        problem_type = request.POST.get('problem_type')
        description = request.POST.get('description')
        steps = request.POST.get('steps')
        urgency = request.POST.get('urgency')
        attachments = request.FILES.get('attachments')
        
        # Here you can add email or database saving logic
        messages.success(request, 'Thank you for reporting this issue. Our team will investigate it promptly.')
        return redirect('report_problem')
    
    return render(request, 'support/report_problem.html')
    return render(request, 'support/report_problem.html')