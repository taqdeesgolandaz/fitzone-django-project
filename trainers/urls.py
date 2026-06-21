from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.trainer_list, name='list'),
    path('<int:trainer_id>/', views.trainer_detail, name='detail'),
    path('book/<int:trainer_id>/', views.book_session, name='book'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('cancel/<int:session_id>/', views.cancel_session, name='cancel'),
    path('review/<int:trainer_id>/', views.add_review, name='add_review'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('admin/reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('admin/complete/<int:booking_id>/', views.mark_completed, name='mark_completed'),
]