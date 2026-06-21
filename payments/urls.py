from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Membership payment
    path('history/', views.payment_history, name='payment_history'),
    path('download-invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
    path('check-status/<str:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    
    # Trainer session payment
    path('initiate-session-payment/<int:session_id>/', views.initiate_session_payment, name='initiate_session_payment'),
    path('create-session-order/<int:session_id>/', views.create_session_order, name='create_session_order'),
    path('verify-session-payment/', views.verify_session_payment, name='verify_session_payment'),
]