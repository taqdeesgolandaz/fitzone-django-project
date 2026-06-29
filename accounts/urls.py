from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import (
    RegisterView, LoginView, LogoutView, UserProfileView, 
    ChangePasswordView, UserDetailView,
    login_view, register_view, dashboard_view, logout_view
)

urlpatterns = [
    # Template URLs (for web browser)
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('auto-admin-login/', views.auto_admin_login, name='auto_admin_login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('set-language/', views.set_language, name='set_language'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('api/csrf-token/', views.get_csrf_token, name='csrf_token'),

    # API URLs (for mobile app / React frontend)
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('api/me/', UserDetailView.as_view(), name='api_user_detail'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
    path('help-center/', views.help_center_view, name='help_center'),
    path('contact-support/', views.contact_support_view, name='contact_support'),
    path('report-problem/', views.report_problem_view, name='report_problem'),
]