from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Membership payment
    path('upgrade/', views.upgrade_membership, name='upgrade_membership'),
    path('create-upgrade-order/', views.create_upgrade_order, name='create_upgrade_order'),
    path('verify-upgrade-payment/', views.verify_upgrade_payment, name='verify_upgrade_payment'),
    path('process-free-upgrade/', views.process_free_upgrade, name='process_free_upgrade'),
    path('history/', views.payment_history, name='payment_history'),
    path('download-invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('initiate-membership/<int:plan_id>/', views.upi_payment, name='upi_payment'),
    
    # Trainer session payment
    path('initiate-session-payment/<int:session_id>/', views.initiate_session_payment, name='initiate_session_payment'),
    path('create-session-order/<int:session_id>/', views.create_session_order, name='create_session_order'),
    path('verify-session-payment/', views.verify_session_payment, name='verify_session_payment'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
]