from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('contact-support/', views.contact_support_view, name='contact_support'),
    path('report-problem/', views.report_problem_view, name='report_problem'),
    path('report-success/', views.report_success_view, name='report_success'),
    path('success/', views.success_view, name='success'),
    path('error/', views.error_view, name='error'),
    path('faq/', views.faq_view, name='faq'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
    path('admin/messages/', views.admin_messages_view, name='admin_messages'),
    path('admin/message/<int:message_id>/', views.admin_message_detail, name='admin_message_detail'),
    path('admin/message/<int:message_id>/delete/', views.admin_message_delete, name='admin_message_delete'),
]